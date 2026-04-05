"""OpenEnv-compliant environment for Email Triage & Response."""

from __future__ import annotations

from src.models import Action, Observation, RewardDetail, State, StepResult
from src.tasks.email_classify import EmailClassifyTask
from src.tasks.email_respond import EmailRespondTask
from src.tasks.email_thread import EmailThreadTask
from src.graders.classify_grader import grade_classification
from src.graders.respond_grader import grade_response
from src.graders.thread_grader import grade_thread_step, grade_thread_resolution
from src.reward import apply_edge_case_penalties


class EmailTriageEnv:
    """
    A real-world OpenEnv environment for email triage and response.

    Three tasks with increasing difficulty:
      - email_classify (easy): classify email by priority + category
      - email_respond (medium): draft professional reply to complaint
      - email_thread (hard): multi-turn thread resolution with contradictions

    Implements the full OpenEnv interface: step(action), reset(), state().
    
    Innovative features:
      - Curriculum Learning: Auto-unlock harder tasks based on performance
      - Email Similarity Avoidance: Tracks seen emails to prevent repetition
      - Adaptive Difficulty: Escalates to harder tasks when agent excels
    """

    TASK_CLASSES = {
        "email_classify": EmailClassifyTask,
        "email_respond": EmailRespondTask,
        "email_thread": EmailThreadTask,
    }
    
    # Curriculum thresholds for task unlocking
    CURRICULUM_THRESHOLDS = {
        "email_classify": 0.0,   # Always unlocked
        "email_respond": 0.70,   # Unlock when classify avg >= 0.70
        "email_thread": 0.65,    # Unlock when respond avg >= 0.65
    }

    def __init__(
        self,
        adaptive_difficulty: bool = True,
        curriculum_mode: bool = True,
        avoid_repetition: bool = True,
    ):
        self._task = None
        self._task_id: str = ""
        self._step: int = 0
        self._max_steps: int = 1
        self._done: bool = True
        self._rewards: list[float] = []
        self._total_reward: float = 0.0
        self._observation: Observation | None = None
        self._adaptive = adaptive_difficulty
        self._curriculum_mode = curriculum_mode
        self._avoid_repetition = avoid_repetition
        self._recent_scores: list[float] = []
        self._episode_count: int = 0
        self._task_index: dict[str, int] = {
            "email_classify": 0,
            "email_respond": 0,
            "email_thread": 0,
        }
        
        # Curriculum learning: track per-task scores
        self._task_scores: dict[str, list[float]] = {
            "email_classify": [],
            "email_respond": [],
            "email_thread": [],
        }
        self._unlocked_tasks: set[str] = {"email_classify"}
        
        # Email similarity avoidance: track seen email IDs per task
        self._seen_emails: dict[str, set[str]] = {
            "email_classify": set(),
            "email_respond": set(),
            "email_thread": set(),
        }

    def reset(self, task_id: str | None = None, email_index: int | None = None) -> Observation:
        """Reset environment and start a new episode.

        Args:
            task_id: which task to run ("email_classify", "email_respond", "email_thread").
                     If None, picks based on adaptive difficulty.
            email_index: specific email/thread index. If None, cycles through data.

        Returns:
            Initial observation for the episode.
        """
        if task_id is None:
            task_id = self._pick_adaptive_task()

        if task_id not in self.TASK_CLASSES:
            raise ValueError(f"Unknown task: {task_id}. Must be one of {list(self.TASK_CLASSES)}")
        
        # Curriculum mode: check if task is unlocked
        if self._curriculum_mode and task_id not in self._unlocked_tasks:
            # Fall back to the highest unlocked task
            task_id = self._get_highest_unlocked_task()

        task_cls = self.TASK_CLASSES[task_id]
        self._task = task_cls(seed=self._episode_count)
        self._task_id = task_id
        self._step = 0
        self._done = False
        self._rewards = []
        self._total_reward = 0.0
        self._episode_count += 1

        # Email similarity avoidance: pick an unseen email if possible
        idx = email_index if email_index is not None else self._pick_unseen_email(task_id)
        self._task.pick_email(index=idx)
        
        # Track seen email
        if self._avoid_repetition:
            email_id = self._get_current_email_id()
            if email_id:
                self._seen_emails[task_id].add(email_id)
        
        if email_index is None:
            self._task_index[task_id] += 1

        self._max_steps = self._task.max_steps
        self._observation = self._task.build_observation(step=0)
        return self._observation
    
    def _pick_unseen_email(self, task_id: str) -> int:
        """Pick an email index that hasn't been seen yet (similarity avoidance)."""
        if not self._avoid_repetition:
            return self._task_index[task_id]
        
        from src.data.emails import CLASSIFY_EMAILS, RESPOND_EMAILS, THREAD_SCENARIOS
        
        email_pools = {
            "email_classify": CLASSIFY_EMAILS,
            "email_respond": RESPOND_EMAILS,
            "email_thread": THREAD_SCENARIOS,
        }
        
        pool = email_pools.get(task_id, [])
        seen = self._seen_emails.get(task_id, set())
        
        # Find first unseen email
        for i, email in enumerate(pool):
            email_id = email.id if hasattr(email, "id") else str(i)
            if email_id not in seen:
                return i
        
        # All emails seen - reset tracking and start over
        self._seen_emails[task_id] = set()
        return 0
    
    def _get_current_email_id(self) -> str | None:
        """Get the ID of the current email/thread."""
        if self._task is None:
            return None
        if hasattr(self._task, "current_email") and self._task.current_email:
            return self._task.current_email.id
        if hasattr(self._task, "current_thread") and self._task.current_thread:
            return self._task.current_thread.id
        return None
    
    def _get_highest_unlocked_task(self) -> str:
        """Get the most difficult unlocked task."""
        task_order = ["email_thread", "email_respond", "email_classify"]
        for task in task_order:
            if task in self._unlocked_tasks:
                return task
        return "email_classify"
    
    def _update_curriculum(self) -> None:
        """Update curriculum unlocks based on task performance."""
        if not self._curriculum_mode:
            return
        
        # Check if email_respond should be unlocked
        classify_scores = self._task_scores["email_classify"]
        if len(classify_scores) >= 3:
            avg = sum(classify_scores[-5:]) / len(classify_scores[-5:])
            if avg >= self.CURRICULUM_THRESHOLDS["email_respond"]:
                self._unlocked_tasks.add("email_respond")
        
        # Check if email_thread should be unlocked
        respond_scores = self._task_scores["email_respond"]
        if len(respond_scores) >= 3:
            avg = sum(respond_scores[-5:]) / len(respond_scores[-5:])
            if avg >= self.CURRICULUM_THRESHOLDS["email_thread"]:
                self._unlocked_tasks.add("email_thread")

    def step(self, action: Action) -> StepResult:
        """Execute one step in the environment.

        Args:
            action: the agent's response.

        Returns:
            StepResult with observation, reward, done flag, and info dict.
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        if self._task is None:
            raise RuntimeError("No task initialized. Call reset() first.")

        response = action.message
        reward_detail = self._grade_step(response)
        reward_detail = apply_edge_case_penalties(response, reward_detail)

        reward = reward_detail.total
        self._rewards.append(reward)
        self._total_reward = sum(self._rewards) / len(self._rewards)
        self._step += 1

        # For multi-turn tasks, record the response
        if hasattr(self._task, "record_response"):
            self._task.record_response(response)

        if self._step >= self._max_steps:
            self._done = True

        # Build next observation (or final one)
        if not self._done:
            self._observation = self._task.build_observation(step=self._step)
        else:
            # Final observation repeats the last one
            self._recent_scores.append(self._total_reward)
            if len(self._recent_scores) > 10:
                self._recent_scores = self._recent_scores[-10:]
            
            # Track per-task scores for curriculum learning
            self._task_scores[self._task_id].append(self._total_reward)
            if len(self._task_scores[self._task_id]) > 10:
                self._task_scores[self._task_id] = self._task_scores[self._task_id][-10:]
            
            # Update curriculum unlocks
            self._update_curriculum()

        info = {
            "reward_detail": reward_detail.model_dump(),
            "step": self._step,
            "total_reward": round(self._total_reward, 2),
            "task_id": self._task_id,
            "curriculum": {
                "unlocked_tasks": list(self._unlocked_tasks),
                "task_averages": {
                    task: round(sum(scores[-5:]) / max(len(scores[-5:]), 1), 2)
                    for task, scores in self._task_scores.items()
                    if scores
                },
            },
        }

        return StepResult(
            observation=self._observation,
            reward=reward,
            done=self._done,
            info=info,
        )

    def state(self) -> State:
        """Return current environment state."""
        return State(
            task_id=self._task_id or "none",
            task_name=self._task.task_name if self._task else "none",
            difficulty=self._task.difficulty if self._task else "none",
            step=self._step,
            max_steps=self._max_steps,
            done=self._done,
            total_reward=round(self._total_reward, 2),
            rewards=[round(r, 2) for r in self._rewards],
            metadata={
                "episode_count": self._episode_count,
                "recent_avg_score": round(
                    sum(self._recent_scores) / max(len(self._recent_scores), 1), 2
                ),
                "adaptive_difficulty": self._adaptive,
                "curriculum_mode": self._curriculum_mode,
                "unlocked_tasks": list(self._unlocked_tasks),
                "seen_emails": {k: len(v) for k, v in self._seen_emails.items()},
            },
        )

    def close(self) -> None:
        """Clean up resources."""
        self._task = None
        self._done = True

    def _grade_step(self, response: str) -> RewardDetail:
        """Route to the appropriate grader based on task type."""
        if self._task_id == "email_classify":
            return grade_classification(response, self._task.current_email)
        elif self._task_id == "email_respond":
            return grade_response(response, self._task.current_email)
        elif self._task_id == "email_thread":
            return grade_thread_step(
                self._step, response, self._task.current_thread
            )
        else:
            raise ValueError(f"No grader for task: {self._task_id}")

    def _pick_adaptive_task(self) -> str:
        """Pick task based on recent performance. Higher scores → harder tasks."""
        if not self._adaptive or len(self._recent_scores) < 2:
            return "email_classify"

        avg = sum(self._recent_scores[-5:]) / len(self._recent_scores[-5:])

        if avg > 0.8:
            return "email_thread"
        elif avg > 0.5:
            return "email_respond"
        else:
            return "email_classify"
