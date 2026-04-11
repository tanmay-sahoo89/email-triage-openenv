"""
Analytics & Metrics Module for Email Triage OpenEnv
====================================================
Provides real-time performance tracking, multi-agent benchmarking,
and impact metrics for production monitoring and research.
"""

import json
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class PerformanceTracker:
    """Track per-task performance metrics, learning curves, and anomalies."""

    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.episodes: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.task_stats: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {
                "total_episodes": 0,
                "total_successes": 0,
                "avg_reward": 0.0,
                "avg_steps": 0.0,
                "min_reward": 1.0,
                "max_reward": 0.0,
                "success_rate": 0.0,
                "improvement_trend": 0.0,
            }
        )
        self.timestamps: Dict[str, List[float]] = defaultdict(list)

    def record_episode(
        self, task_id: str, reward: float, steps: int, success: bool, duration: float
    ) -> None:
        """Record a completed episode."""
        self.episodes[task_id].append(
            {
                "reward": reward,
                "steps": steps,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "duration": duration,
            }
        )

        stats = self.task_stats[task_id]
        stats["total_episodes"] += 1
        stats["total_successes"] += success
        stats["success_rate"] = stats["total_successes"] / stats["total_episodes"]

        rewards = [ep["reward"] for ep in self.episodes[task_id]]
        steps_list = [ep["steps"] for ep in self.episodes[task_id]]

        stats["avg_reward"] = float(np.mean(rewards))
        stats["min_reward"] = float(np.min(rewards))
        stats["max_reward"] = float(np.max(rewards))
        stats["avg_steps"] = float(np.mean(steps_list))

        if len(rewards) >= 2:
            first_half = np.mean(rewards[: len(rewards) // 2])
            second_half = np.mean(rewards[len(rewards) // 2 :])
            stats["improvement_trend"] = float(second_half - first_half)

    def get_task_stats(self, task_id: str) -> Dict[str, Any]:
        """Get aggregated statistics for a task."""
        return self.task_stats.get(task_id, {})

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all tasks."""
        return dict(self.task_stats)

    def detect_anomalies(self, task_id: str, threshold: float = 2.0) -> List[Dict]:
        """Detect anomalous episodes (outliers) using Z-score."""
        episodes = self.episodes[task_id]
        if len(episodes) < 3:
            return []

        rewards = np.array([ep["reward"] for ep in episodes])
        mean = np.mean(rewards)
        std = np.std(rewards)

        if std == 0:
            return []

        z_scores = np.abs((rewards - mean) / std)
        anomalies = []

        for i, (episode, z_score) in enumerate(zip(episodes, z_scores)):
            if z_score > threshold:
                anomalies.append(
                    {
                        "episode_index": i,
                        "reward": episode["reward"],
                        "z_score": float(z_score),
                        "type": "low" if episode["reward"] < mean else "high",
                    }
                )

        return anomalies

    def get_learning_curve(self, task_id: str, smooth_window: int = 5) -> List[float]:
        """Get smoothed learning curve for visualization."""
        episodes = self.episodes[task_id]
        if not episodes:
            return []

        rewards = [ep["reward"] for ep in episodes]

        if len(rewards) < smooth_window:
            return rewards

        smoothed = []
        for i in range(len(rewards) - smooth_window + 1):
            window = rewards[i : i + smooth_window]
            smoothed.append(float(np.mean(window)))

        return smoothed


class MultiAgentBenchmark:
    """Track and compare performance across multiple agents."""

    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.rankings: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self.expert_baseline = {
            "email_classify": 0.92,
            "email_respond": 0.85,
            "email_thread": 0.78,
            "email_investigate": 0.75,
            "email_workflow": 0.70,
        }

    def register_agent(self, agent_id: str, model_name: str) -> None:
        """Register a new agent."""
        self.agents[agent_id] = {
            "model_name": model_name,
            "tasks": defaultdict(list),
            "registered_at": datetime.now().isoformat(),
        }

    def record_agent_result(
        self, agent_id: str, task_id: str, reward: float, steps: int
    ) -> None:
        """Record an agent's performance on a task."""
        if agent_id not in self.agents:
            self.register_agent(agent_id, "unknown")

        self.agents[agent_id]["tasks"][task_id].append(
            {"reward": reward, "steps": steps, "timestamp": datetime.now().isoformat()}
        )

    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get aggregated stats for an agent."""
        if agent_id not in self.agents:
            return {}

        agent = self.agents[agent_id]
        task_scores = {}

        for task_id, results in agent["tasks"].items():
            rewards = [r["reward"] for r in results]
            task_scores[task_id] = {
                "avg_reward": float(np.mean(rewards)),
                "episodes": len(results),
                "vs_baseline": float(np.mean(rewards) - self.expert_baseline.get(task_id, 0.0)),
            }

        overall_avg = np.mean([s["avg_reward"] for s in task_scores.values()]) if task_scores else 0

        return {
            "agent_id": agent_id,
            "model_name": agent["model_name"],
            "registered_at": agent["registered_at"],
            "task_scores": task_scores,
            "overall_avg": float(overall_avg),
        }

    def get_rankings(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Get agent rankings (by task or overall)."""
        if task_id:
            rankings = []
            for agent_id, agent in self.agents.items():
                if task_id in agent["tasks"]:
                    rewards = [r["reward"] for r in agent["tasks"][task_id]]
                    avg = np.mean(rewards)
                    rankings.append((agent_id, float(avg)))
            rankings.sort(key=lambda x: x[1], reverse=True)
            return {
                "task_id": task_id,
                "rankings": [{"agent_id": aid, "avg_reward": score} for aid, score in rankings],
            }
        else:
            rankings = []
            for agent_id in self.agents:
                stats = self.get_agent_stats(agent_id)
                rankings.append((agent_id, stats["overall_avg"]))
            rankings.sort(key=lambda x: x[1], reverse=True)
            return {
                "scope": "overall",
                "rankings": [{"agent_id": aid, "overall_avg": score} for aid, score in rankings],
            }

    def compare_agents(self, agent_ids: List[str]) -> Dict[str, Any]:
        """Detailed comparison of specific agents."""
        comparison = {"timestamp": datetime.now().isoformat(), "agents": {}}

        for agent_id in agent_ids:
            if agent_id in self.agents:
                comparison["agents"][agent_id] = self.get_agent_stats(agent_id)

        return comparison


class ImpactMetrics:
    """Calculate business impact metrics."""

    def __init__(self):
        self.fraud_prevented_emails = 0
        self.customer_satisfaction_score = 0.0
        self.avg_response_time_saved = 0.0  # seconds
        self.successful_resolutions = 0
        self.total_episodes = 0

    def record_episode_impact(
        self,
        task_id: str,
        reward: float,
        phishing_detected: bool = False,
        resolution_quality: float = 0.0,
    ) -> None:
        """Record impact metrics from an episode."""
        self.total_episodes += 1

        if phishing_detected:
            self.fraud_prevented_emails += 1

        if task_id == "email_respond":
            self.customer_satisfaction_score = (
                self.customer_satisfaction_score * 0.9 + reward * 0.1
            )
            self.avg_response_time_saved += (
                reward * 45  # Assuming 45 seconds saved per good response
            )

        if reward > 0.75:
            self.successful_resolutions += 1

    def get_impact_report(self) -> Dict[str, Any]:
        """Generate business impact report."""
        return {
            "fraud_prevented_emails": self.fraud_prevented_emails,
            "fraud_prevented_value_usd": self.fraud_prevented_emails * 250,  # $250 avg per fraud
            "customer_satisfaction_score": float(self.customer_satisfaction_score),
            "total_hours_saved": self.avg_response_time_saved / 3600,
            "hours_saved_value_usd": (self.avg_response_time_saved / 3600) * 35,  # $35/hr
            "successful_resolutions": self.successful_resolutions,
            "resolution_rate": (
                self.successful_resolutions / self.total_episodes if self.total_episodes > 0 else 0
            ),
            "total_episodes": self.total_episodes,
            "estimated_total_value_usd": (self.fraud_prevented_emails * 250)
            + ((self.avg_response_time_saved / 3600) * 35),
        }


class ExplainabilityReport:
    """Generate explainability reports for agent decisions."""

    def __init__(self):
        self.decision_history: List[Dict[str, Any]] = []

    def log_decision(
        self,
        episode_id: str,
        task_id: str,
        agent_response: str,
        reward: float,
        grading_details: Dict[str, Any],
    ) -> None:
        """Log a decision with grading breakdown."""
        self.decision_history.append(
            {
                "episode_id": episode_id,
                "task_id": task_id,
                "agent_response": agent_response,
                "reward": reward,
                "grading_details": grading_details,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def explain_episode(self, episode_id: str) -> Dict[str, Any]:
        """Get detailed explanation for an episode."""
        for decision in self.decision_history:
            if decision["episode_id"] == episode_id:
                return {
                    "episode_id": episode_id,
                    "task_id": decision["task_id"],
                    "agent_response": decision["agent_response"],
                    "final_reward": decision["reward"],
                    "grading_criteria": decision["grading_details"],
                    "why_this_score": self._generate_explanation(decision),
                }
        return {"error": "Episode not found"}

    def _generate_explanation(self, decision: Dict[str, Any]) -> str:
        """Generate human-readable explanation."""
        task_id = decision["task_id"]
        reward = decision["reward"]
        details = decision["grading_details"]

        explanations = []

        if task_id == "email_classify":
            if reward > 0.8:
                explanations.append(
                    "✅ Agent correctly classified priority and category with high confidence."
                )
            elif reward > 0.5:
                explanations.append(
                    "⚠️ Agent got one criterion correct, but missed the other."
                )
            else:
                explanations.append("❌ Agent failed to identify priority or category.")

            if "phishing_bonus" in details and details["phishing_bonus"]:
                explanations.append("🎯 Bonus: Agent correctly detected phishing attempt!")

        elif task_id == "email_respond":
            if reward > 0.7:
                explanations.append(
                    "✅ Response was professional, empathetic, and well-structured."
                )
            else:
                explanations.append(
                    f"⚠️ Response needs improvement: {details.get('notes', 'check tone and relevance')}"
                )

        return " ".join(explanations)

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent decisions."""
        return self.decision_history[-limit:]


# Global singletons for easy access
_perf_tracker = PerformanceTracker()
_benchmark = MultiAgentBenchmark()
_impact = ImpactMetrics()
_explainability = ExplainabilityReport()


def get_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker."""
    return _perf_tracker


def get_benchmark() -> MultiAgentBenchmark:
    """Get the global benchmark."""
    return _benchmark


def get_impact_metrics() -> ImpactMetrics:
    """Get the global impact metrics."""
    return _impact


def get_explainability() -> ExplainabilityReport:
    """Get the global explainability reporter."""
    return _explainability
