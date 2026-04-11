"""
Multi-Task Learning Orchestrator
==================================
Orchestrates learning across multiple tasks to show transfer learning effects.
Demonstrates how skills learned in one task help performance in related tasks.
"""

from typing import Dict, List, Tuple
from datetime import datetime
import numpy as np


class TransferLearningAnalyzer:
    """Analyze transfer learning effects across tasks."""

    def __init__(self):
        self.task_prerequisites = {
            "email_classify": [],
            "email_respond": ["email_classify"],
            "email_thread": ["email_classify", "email_respond"],
            "email_investigate": ["email_thread"],
            "email_workflow": ["email_investigate", "email_respond"],
        }
        self.skill_transfer = {
            "classification_skill": 0.3,  # Helps respond by 30%
            "empathy_skill": 0.25,  # Helps thread by 25%
            "analysis_skill": 0.4,  # Helps investigate by 40%
            "decision_skill": 0.35,  # Helps workflow by 35%
        }
        self.agent_task_history: Dict[str, Dict] = {}

    def register_agent_learning(self, agent_id: str, task_id: str, reward: float) -> Dict:
        """Register agent learning event and calculate transfer effects."""
        if agent_id not in self.agent_task_history:
            self.agent_task_history[agent_id] = {"tasks": {}, "skills_acquired": {}}

        if task_id not in self.agent_task_history[agent_id]["tasks"]:
            self.agent_task_history[agent_id]["tasks"][task_id] = {
                "episodes": 0,
                "avg_reward": 0.0,
                "total_reward": 0.0,
            }

        task_data = self.agent_task_history[agent_id]["tasks"][task_id]
        task_data["episodes"] += 1
        task_data["total_reward"] += reward
        task_data["avg_reward"] = task_data["total_reward"] / task_data["episodes"]

        # Extract skills from task performance
        skills = self._extract_skills(task_id, reward)
        for skill, level in skills.items():
            if skill not in self.agent_task_history[agent_id]["skills_acquired"]:
                self.agent_task_history[agent_id]["skills_acquired"][skill] = 0.0
            self.agent_task_history[agent_id]["skills_acquired"][skill] = max(
                self.agent_task_history[agent_id]["skills_acquired"][skill], level
            )

        return {
            "agent_id": agent_id,
            "task_id": task_id,
            "direct_reward": reward,
            "skills_acquired": skills,
            "transfer_bonus": self._calculate_transfer_bonus(agent_id),
        }

    def _extract_skills(self, task_id: str, reward: float) -> Dict[str, float]:
        """Extract learned skills from task performance."""
        skills = {}

        if task_id == "email_classify":
            skills["classification_skill"] = reward
        elif task_id == "email_respond":
            skills["empathy_skill"] = reward * 0.8
            skills["communication_skill"] = reward
        elif task_id == "email_thread":
            skills["empathy_skill"] = reward * 0.7
            skills["analysis_skill"] = reward * 0.9
        elif task_id == "email_investigate":
            skills["analysis_skill"] = reward * 0.95
            skills["decision_skill"] = reward
        elif task_id == "email_workflow":
            skills["decision_skill"] = reward * 0.9
            skills["coordination_skill"] = reward

        return skills

    def _calculate_transfer_bonus(self, agent_id: str) -> float:
        """Calculate performance bonus from skill transfer."""
        agent = self.agent_task_history.get(agent_id, {})
        skills = agent.get("skills_acquired", {})

        bonus = 0.0
        if "classification_skill" in skills:
            bonus += skills["classification_skill"] * self.skill_transfer.get(
                "classification_skill", 0
            )
        if "empathy_skill" in skills:
            bonus += skills["empathy_skill"] * self.skill_transfer.get("empathy_skill", 0)
        if "analysis_skill" in skills:
            bonus += skills["analysis_skill"] * self.skill_transfer.get("analysis_skill", 0)

        return min(bonus, 0.25)  # Cap transfer bonus at 25%

    def get_learning_pathway(self, agent_id: str) -> Dict:
        """Get recommended learning pathway based on current progress."""
        if agent_id not in self.agent_task_history:
            return {
                "agent_id": agent_id,
                "recommended_pathway": list(self.task_prerequisites.keys()),
                "rationale": "New agent - start with fundamentals",
            }

        agent = self.agent_task_history[agent_id]
        completed_tasks = set(agent["tasks"].keys())
        completed_scores = {
            task: data["avg_reward"]
            for task, data in agent["tasks"].items()
        }

        # Find next best task
        next_tasks = []
        for task, prerequisites in self.task_prerequisites.items():
            if task not in completed_tasks:
                if all(prereq in completed_tasks for prereq in prerequisites):
                    next_tasks.append(task)

        # Recommend highest value next task
        if next_tasks:
            recommended = next_tasks[0]
            rationale = f"Prerequisites met. Transfer bonus available from {prerequisites}"
        else:
            recommended = "email_workflow"  # Default
            rationale = "Consider advanced tasks or retry for improvement"

        return {
            "agent_id": agent_id,
            "completed_tasks": list(completed_tasks),
            "task_scores": completed_scores,
            "recommended_next_task": recommended,
            "rationale": rationale,
            "total_skills_acquired": len(agent["skills_acquired"]),
            "estimated_transfer_boost": self._calculate_transfer_bonus(agent_id),
        }

    def compare_learning_pathways(self, agent_ids: List[str]) -> Dict:
        """Compare learning efficiency across agents."""
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "most_efficient": None,
            "best_at_transfer": None,
        }

        efficiencies = {}
        transfer_scores = {}

        for agent_id in agent_ids:
            if agent_id in self.agent_task_history:
                agent = self.agent_task_history[agent_id]
                total_episodes = sum(t["episodes"] for t in agent["tasks"].values())
                avg_reward = np.mean([t["avg_reward"] for t in agent["tasks"].values()])
                efficiency = avg_reward / max(total_episodes, 1)  # Reward per episode
                transfer_score = self._calculate_transfer_bonus(agent_id)

                comparison["agents"][agent_id] = {
                    "tasks_completed": len(agent["tasks"]),
                    "total_episodes": total_episodes,
                    "avg_reward": float(avg_reward),
                    "learning_efficiency": float(efficiency),
                    "transfer_score": float(transfer_score),
                    "skills_acquired": len(agent["skills_acquired"]),
                }

                efficiencies[agent_id] = efficiency
                transfer_scores[agent_id] = transfer_score

        if efficiencies:
            comparison["most_efficient"] = max(efficiencies, key=efficiencies.get)
        if transfer_scores:
            comparison["best_at_transfer"] = max(transfer_scores, key=transfer_scores.get)

        return comparison

    def get_skill_matrix(self, agent_id: str) -> Dict[str, Dict]:
        """Get agent's skill acquisition matrix."""
        if agent_id not in self.agent_task_history:
            return {"agent_id": agent_id, "skills": {}, "total_skill_level": 0.0}

        agent = self.agent_task_history[agent_id]
        skills = agent.get("skills_acquired", {})

        total_skill = sum(skills.values())

        return {
            "agent_id": agent_id,
            "skills": {
                skill: float(level) for skill, level in skills.items()
            },
            "total_skill_level": float(total_skill),
            "skill_distribution": {
                skill: float(level / total_skill) if total_skill > 0 else 0.0
                for skill, level in skills.items()
            },
            "recommended_focus": max(
                ((k, v) for k, v in skills.items()),
                key=lambda x: x[1],
                default=(None, 0.0),
            )[0],
        }


class CurriculumOptimizer:
    """Optimize curriculum learning pathways for agents."""

    def __init__(self):
        self.agent_profiles: Dict[str, Dict] = {}

    def optimize_for_agent(self, agent_id: str, initial_performance: float) -> List[str]:
        """Generate optimized curriculum based on agent capabilities."""
        if initial_performance < 0.3:
            return ["email_classify"]  # Start with basics
        elif initial_performance < 0.6:
            return ["email_classify", "email_respond"]
        elif initial_performance < 0.8:
            return ["email_respond", "email_thread", "email_investigate"]
        else:
            return ["email_thread", "email_investigate", "email_workflow"]

    def predict_task_success(self, agent_id: str, task_id: str, history: Dict) -> float:
        """Predict success probability for a task given agent history."""
        if not history:
            return 0.5  # Default uncertainty

        avg_performance = np.mean(list(history.values()))

        # Task difficulty multipliers
        difficulty = {
            "email_classify": 1.0,
            "email_respond": 0.85,
            "email_thread": 0.7,
            "email_investigate": 0.6,
            "email_workflow": 0.5,
        }

        predicted = avg_performance * difficulty.get(task_id, 0.7)
        return min(max(predicted, 0.01), 0.99)  # Clamp to valid range

    def recommend_curriculum(
        self, agent_id: str, target_tasks: List[str], current_performance: Dict
    ) -> Dict:
        """Recommend optimal task sequence to reach target tasks."""
        curriculum = []
        current_perf = np.mean(list(current_performance.values())) if current_performance else 0.5

        # Map task dependencies
        deps = {
            "email_classify": [],
            "email_respond": ["email_classify"],
            "email_thread": ["email_classify", "email_respond"],
            "email_investigate": ["email_thread"],
            "email_workflow": ["email_investigate", "email_respond"],
        }

        # Build path to first target
        visited = set()
        for target in target_tasks:
            path = self._build_dependency_path(target, deps)
            curriculum.extend([t for t in path if t not in visited])
            visited.update(path)

        return {
            "agent_id": agent_id,
            "target_tasks": target_tasks,
            "recommended_curriculum": curriculum,
            "current_performance": float(current_perf),
            "estimated_completion_episodes": len(curriculum) * (10 / current_perf)
            if current_perf > 0
            else 100,
        }

    def _build_dependency_path(self, task: str, deps: Dict) -> List[str]:
        """Build path of dependencies for a task."""
        path = []
        for dep in deps.get(task, []):
            path.extend(self._build_dependency_path(dep, deps))
        path.append(task)
        return path


# Global instances for easy access
_transfer_analyzer = TransferLearningAnalyzer()
_curriculum_optimizer = CurriculumOptimizer()


def get_transfer_analyzer() -> TransferLearningAnalyzer:
    """Get the global transfer learning analyzer."""
    return _transfer_analyzer


def get_curriculum_optimizer() -> CurriculumOptimizer:
    """Get the global curriculum optimizer."""
    return _curriculum_optimizer
