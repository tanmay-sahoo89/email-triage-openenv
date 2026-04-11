"""OpenEnv-compliant environment for Email Triage & Response."""

from __future__ import annotations

from src.models import (
    Action,
    Observation,
    RewardDetail,
    State,
    StepResult,
    ToolCall,
)
from src.tasks.email_classify import EmailClassifyTask
from src.tasks.email_respond import EmailRespondTask
from src.tasks.email_thread import EmailThreadTask
from src.tasks.email_investigate import EmailInvestigateTask
from src.tasks.email_triage_workflow import EmailTriageWorkflowTask
from src.graders.classify_grader import grade_classification
from src.graders.respond_grader import grade_response
from src.graders.thread_grader import grade_thread_step
from src.graders.investigate_grader import grade_investigation
from src.graders.workflow_grader import grade_workflow
from src.reward import apply_edge_case_penalties
from src.tools import parse_tool_calls


class EmailTriageEnv:
    """Real-world OpenEnv environment for email triage and response.

    Five tasks spanning increasing agentic complexity:

      - email_classify          (easy)   — single-turn classification
      - email_respond           (medium) — single-turn response drafting
      - email_thread            (hard)   — 4-step thread resolution
      - email_investigate       (hard)   — multi-step tool-using investigation
      - email_triage_workflow   (hard)   — full end-to-end workflow w/ actions

    Implements the OpenEnv HTTP interface: reset(), step(action), state(),
    close(). Preserves every field ``info`` already carried so the v1.x
    clients keep working.
    """

    TASK_CLASSES = {
        "email_classify": EmailClassifyTask,
        "email_respond": EmailRespondTask,
        "email_thread": EmailThreadTask,
        "email_investigate": EmailInvestigateTask,
        "email_triage_workflow": EmailTriageWorkflowTask,
    }

    # Curriculum thresholds for task unlocking
    CURRICULUM_THRESHOLDS = {
        "email_classify": 0.0,        # Always unlocked
        "email_respond": 0.70,        # Requires 70% avg on classify
        "email_thread": 0.65,         # Requires 65% avg on respond
        "email_investigate": 0.60,    # Requires 60% avg on respond
        "email_triage_workflow": 0.55, # Requires 55% avg on classify + respond
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
        self._task_index: dict[str, int] = {k: 0 for k in self.TASK_CLASSES}
        self._bypass_curriculum_next = False  # NEW: Skip curriculum check for next reset

        self._task_scores: dict[str, list[float]] = {k: [] for k in self.TASK_CLASSES}
        self._unlocked_tasks: set[str] = {"email_classify"}
        self._seen_emails: dict[str, set[str]] = {k: set() for k in self.TASK_CLASSES}

    def reset(self, task_id: str | None = None, email_index: int | None = None) -> Observation:
        if task_id is None:
            task_id = self._pick_adaptive_task()

        if task_id not in self.TASK_CLASSES:
            raise ValueError(
                f"Unknown task: {task_id}. Must be one of {list(self.TASK_CLASSES)}"
            )

        # Curriculum mode: check if task is unlocked (unless bypassing for this reset)
        if self._curriculum_mode and not self._bypass_curriculum_next and task_id not in self._unlocked_tasks:
            task_id = self._get_highest_unlocked_task()
        
        # Reset the bypass flag
        self._bypass_curriculum_next = False

        task_cls = self.TASK_CLASSES[task_id]
        self._task = task_cls(seed=self._episode_count)
        self._task_id = task_id
        self._step = 0
        self._done = False
        self._rewards = []
        self._total_reward = 0.0
        self._episode_count += 1

        idx = email_index if email_index is not None else self._pick_unseen_email(task_id)
        self._task.pick_email(index=idx)

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
        if not self._avoid_repetition:
            return self._task_index[task_id]

        from src.data.emails import CLASSIFY_EMAILS, RESPOND_EMAILS, THREAD_SCENARIOS
        from src.data.investigations import INVESTIGATION_SCENARIOS
        from src.data.workflows import WORKFLOW_SCENARIOS

        email_pools = {
            "email_classify": CLASSIFY_EMAILS,
            "email_respond": RESPOND_EMAILS,
            "email_thread": THREAD_SCENARIOS,
            "email_investigate": INVESTIGATION_SCENARIOS,
            "email_triage_workflow": WORKFLOW_SCENARIOS,
        }

        pool = email_pools.get(task_id, [])
        seen = self._seen_emails.get(task_id, set())

        for i, item in enumerate(pool):
            # Investigation and workflow scenarios have a nested email
            email_id = getattr(item, "id", None) or str(i)
            if email_id not in seen:
                return i

        self._seen_emails[task_id] = set()
        return 0

    def _get_current_email_id(self) -> str | None:
        if self._task is None:
            return None
        # Investigation / workflow tasks expose current_scenario
        scenario = getattr(self._task, "current_scenario", None)
        if scenario is not None:
            return getattr(scenario, "id", None)
        if hasattr(self._task, "current_email") and getattr(self._task, "_current", None):
            current = self._task._current
            return getattr(current, "id", None)
        if hasattr(self._task, "current_thread") and getattr(self._task, "_current", None):
            return self._task._current.id
        return None

    def _get_highest_unlocked_task(self) -> str:
        task_order = [
            "email_triage_workflow",
            "email_investigate",
            "email_thread",
            "email_respond",
            "email_classify",
        ]
        for task in task_order:
            if task in self._unlocked_tasks:
                return task
        return "email_classify"

    def _update_curriculum(self) -> None:
        if not self._curriculum_mode:
            return

        classify_scores = self._task_scores["email_classify"]
        if len(classify_scores) >= 3:
            avg = sum(classify_scores[-5:]) / len(classify_scores[-5:])
            if avg >= self.CURRICULUM_THRESHOLDS["email_respond"]:
                self._unlocked_tasks.add("email_respond")
            if avg >= self.CURRICULUM_THRESHOLDS["email_triage_workflow"]:
                self._unlocked_tasks.add("email_triage_workflow")

        respond_scores = self._task_scores["email_respond"]
        if len(respond_scores) >= 3:
            avg = sum(respond_scores[-5:]) / len(respond_scores[-5:])
            if avg >= self.CURRICULUM_THRESHOLDS["email_thread"]:
                self._unlocked_tasks.add("email_thread")
            if avg >= self.CURRICULUM_THRESHOLDS["email_investigate"]:
                self._unlocked_tasks.add("email_investigate")

    # ── step ───────────────────────────────────────────────────────────────

    def step(self, action: Action) -> StepResult:
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        if self._task is None:
            raise RuntimeError("No task initialized. Call reset() first.")

        if self._task_id in ("email_investigate", "email_triage_workflow"):
            return self._step_tool_task(action)
        return self._step_text_task(action)

    def _step_text_task(self, action: Action) -> StepResult:
        response = action.message
        reward_detail = self._grade_step(response)
        reward_detail = apply_edge_case_penalties(response, reward_detail)

        reward = reward_detail.total
        self._rewards.append(reward)
        self._total_reward = sum(self._rewards) / len(self._rewards)
        self._step += 1

        if hasattr(self._task, "record_response"):
            self._task.record_response(response)

        if self._step >= self._max_steps:
            self._done = True

        if not self._done:
            self._observation = self._task.build_observation(step=self._step)
        else:
            self._recent_scores.append(self._total_reward)
            if len(self._recent_scores) > 10:
                self._recent_scores = self._recent_scores[-10:]
            self._task_scores[self._task_id].append(self._total_reward)
            if len(self._task_scores[self._task_id]) > 10:
                self._task_scores[self._task_id] = self._task_scores[self._task_id][-10:]
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

    def _step_tool_task(self, action: Action) -> StepResult:
        """Step handler for tool-using tasks.

        The agent's Action can carry structured ``tool_calls`` directly
        (preferred) or a raw message string from which we parse tool calls.
        We execute the tools, update observation, and only grade when the
        task reaches a terminal state (final_verdict submitted, budget
        exhausted, close_ticket called, or max_steps reached).
        """
        tool_calls = list(action.tool_calls)
        if not tool_calls and action.message:
            tool_calls = parse_tool_calls(action.message)

        # Record the reasoning text (for investigate grader)
        if action.message and hasattr(self._task, "record_response"):
            self._task.record_response(action.message)

        # Apply the tool calls
        results = self._task.apply_tool_calls(tool_calls) if tool_calls else []
        self._step += 1

        is_terminal = getattr(self._task, "is_terminal", False)
        if self._step >= self._max_steps:
            is_terminal = True

        reward = 0.0
        reward_detail: RewardDetail

        if not is_terminal:
            # Per-step shaping: small positive reward for every useful tool result
            useful = sum(1 for r in results if r.ok and r.name != "final_verdict")
            reward = min(0.05 * useful, 0.2)
            reward_detail = RewardDetail(
                total=reward,
                breakdown={"intermediate_tool_use": reward},
                feedback=f"Step {self._step}: ran {len(results)} tool call(s)",
            )
            self._rewards.append(reward)
            self._observation = self._task.build_observation(step=self._step)
        else:
            # Terminal: run the full grader
            reward_detail = self._grade_terminal()
            reward = reward_detail.total
            # Replace the per-step accumulation with the terminal score
            # so the reported total reflects overall performance.
            self._rewards.append(reward)
            self._total_reward = reward
            self._done = True
            self._observation = self._task.build_observation(step=self._step)

            self._recent_scores.append(self._total_reward)
            if len(self._recent_scores) > 10:
                self._recent_scores = self._recent_scores[-10:]
            self._task_scores[self._task_id].append(self._total_reward)
            if len(self._task_scores[self._task_id]) > 10:
                self._task_scores[self._task_id] = self._task_scores[self._task_id][-10:]
            self._update_curriculum()

        if not self._done:
            self._total_reward = sum(self._rewards) / max(len(self._rewards), 1)

        info = {
            "reward_detail": reward_detail.model_dump(),
            "step": self._step,
            "total_reward": round(self._total_reward, 2),
            "task_id": self._task_id,
            "tool_results": [r.model_dump() for r in results],
            "tool_budget_remaining": getattr(self._task, "_tool_budget", None),
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

    def _grade_terminal(self) -> RewardDetail:
        """Grade a tool-using task that has reached a terminal state."""
        if self._task_id == "email_investigate":
            return grade_investigation(
                final_verdict=self._task.final_verdict,
                justification=self._task.final_justification,
                tools_called=self._task.tools_called,
                scenario=self._task.current_scenario,
                reasoning_texts=self._task.reasoning_texts,
            )
        elif self._task_id == "email_triage_workflow":
            return grade_workflow(
                actions_taken=self._task.actions_taken,
                classify_args=self._task.classify_args,
                route_args=self._task.route_args,
                sla_hours=self._task.sla_hours,
                escalated=self._task.escalated,
                draft_body=self._task.draft_body,
                closed=self._task.is_terminal,
                scenario=self._task.current_scenario,
            )
        raise ValueError(f"No terminal grader for task: {self._task_id}")

    def state(self) -> State:
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
        self._task = None
        self._done = True

    def bypass_curriculum_for_next_reset(self) -> None:
        """Allow the next reset() call to bypass curriculum constraints."""
        self._bypass_curriculum_next = True

    def _grade_step(self, response: str) -> RewardDetail:
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
        if not self._adaptive or len(self._recent_scores) < 2:
            return "email_classify"

        avg = sum(self._recent_scores[-5:]) / len(self._recent_scores[-5:])

        # When curriculum is OFF, don't check unlocked tasks
        if not self._curriculum_mode:
            if avg > 0.92:
                return "email_triage_workflow"
            if avg > 0.80:
                return "email_thread"
            if avg > 0.85:
                return "email_investigate"
            elif avg > 0.5:
                return "email_respond"
            else:
                return "email_classify"
        
        # When curriculum is ON, respect unlocked tasks
        if avg > 0.92 and "email_triage_workflow" in self._unlocked_tasks:
            return "email_triage_workflow"
        if avg > 0.80 and "email_thread" in self._unlocked_tasks:
            return "email_thread"
        if avg > 0.85 and "email_investigate" in self._unlocked_tasks:
            return "email_investigate"
        elif avg > 0.5 and "email_respond" in self._unlocked_tasks:
            return "email_respond"
        else:
            return "email_classify"
