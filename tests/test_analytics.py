"""Tests for analytics and metrics module."""

import pytest
from src.analytics import (
    PerformanceTracker,
    MultiAgentBenchmark,
    ImpactMetrics,
    ExplainabilityReport,
)


class TestPerformanceTracker:
    """Test performance tracking functionality."""

    def test_track_episode(self):
        """Test recording episode."""
        tracker = PerformanceTracker()
        tracker.record_episode("email_classify", 0.85, 1, True, 0.5)

        stats = tracker.get_task_stats("email_classify")
        assert stats["total_episodes"] == 1
        assert stats["avg_reward"] == 0.85
        assert stats["success_rate"] == 1.0

    def test_multiple_episodes(self):
        """Test aggregation across multiple episodes."""
        tracker = PerformanceTracker()
        tracker.record_episode("email_classify", 0.8, 1, True, 0.5)
        tracker.record_episode("email_classify", 0.9, 1, True, 0.5)

        stats = tracker.get_task_stats("email_classify")
        assert stats["total_episodes"] == 2
        assert abs(stats["avg_reward"] - 0.85) < 0.001
        assert stats["success_rate"] == 1.0

    def test_improvement_trend(self):
        """Test improvement trend calculation."""
        tracker = PerformanceTracker()
        # First half: low scores
        for _ in range(5):
            tracker.record_episode("email_classify", 0.5, 1, False, 0.5)
        # Second half: high scores
        for _ in range(5):
            tracker.record_episode("email_classify", 0.9, 1, True, 0.5)

        stats = tracker.get_task_stats("email_classify")
        assert stats["improvement_trend"] > 0

    def test_learning_curve(self):
        """Test learning curve generation."""
        tracker = PerformanceTracker()
        for i in range(10):
            tracker.record_episode("email_classify", 0.5 + i * 0.05, 1, True, 0.5)

        curve = tracker.get_learning_curve("email_classify", smooth_window=3)
        assert len(curve) > 0
        assert curve[-1] > curve[0]  # Should be increasing

    def test_anomaly_detection(self):
        """Test anomaly detection."""
        tracker = PerformanceTracker()
        # Normal episodes
        for _ in range(10):
            tracker.record_episode("email_classify", 0.75, 1, True, 0.5)
        # Anomaly (very low score)
        tracker.record_episode("email_classify", 0.1, 1, False, 0.5)

        anomalies = tracker.detect_anomalies("email_classify")
        assert len(anomalies) > 0
        assert anomalies[0]["type"] == "low"


class TestMultiAgentBenchmark:
    """Test multi-agent benchmarking."""

    def test_register_agent(self):
        """Test agent registration."""
        benchmark = MultiAgentBenchmark()
        benchmark.register_agent("agent_1", "Qwen2.5-72B")

        stats = benchmark.get_agent_stats("agent_1")
        assert stats["agent_id"] == "agent_1"
        assert stats["model_name"] == "Qwen2.5-72B"

    def test_record_result(self):
        """Test recording agent results."""
        benchmark = MultiAgentBenchmark()
        benchmark.register_agent("agent_1", "Qwen2.5-72B")
        benchmark.record_agent_result("agent_1", "email_classify", 0.85, 1)

        stats = benchmark.get_agent_stats("agent_1")
        assert stats["task_scores"]["email_classify"]["episodes"] == 1
        assert stats["task_scores"]["email_classify"]["avg_reward"] == 0.85

    def test_rankings(self):
        """Test agent ranking generation."""
        benchmark = MultiAgentBenchmark()
        benchmark.register_agent("agent_1", "Model1")
        benchmark.register_agent("agent_2", "Model2")

        benchmark.record_agent_result("agent_1", "email_classify", 0.9, 1)
        benchmark.record_agent_result("agent_2", "email_classify", 0.7, 1)

        rankings = benchmark.get_rankings("email_classify")
        assert rankings["rankings"][0]["agent_id"] == "agent_1"
        assert rankings["rankings"][1]["agent_id"] == "agent_2"

    def test_compare_agents(self):
        """Test agent comparison."""
        benchmark = MultiAgentBenchmark()
        benchmark.register_agent("agent_1", "Model1")
        benchmark.register_agent("agent_2", "Model2")

        benchmark.record_agent_result("agent_1", "email_classify", 0.85, 1)
        benchmark.record_agent_result("agent_2", "email_classify", 0.75, 1)

        comparison = benchmark.compare_agents(["agent_1", "agent_2"])
        assert "agent_1" in comparison["agents"]
        assert "agent_2" in comparison["agents"]


class TestImpactMetrics:
    """Test business impact calculations."""

    def test_fraud_tracking(self):
        """Test fraud prevention tracking."""
        impact = ImpactMetrics()
        impact.record_episode_impact("email_classify", 0.9, phishing_detected=True)

        report = impact.get_impact_report()
        assert report["fraud_prevented_emails"] == 1
        assert report["fraud_prevented_value_usd"] == 250

    def test_satisfaction_score(self):
        """Test customer satisfaction tracking."""
        impact = ImpactMetrics()
        impact.record_episode_impact("email_respond", 0.9)
        impact.record_episode_impact("email_respond", 0.8)

        report = impact.get_impact_report()
        assert report["customer_satisfaction_score"] > 0

    def test_time_saved(self):
        """Test time saved calculation."""
        impact = ImpactMetrics()
        impact.record_episode_impact("email_respond", 0.9)

        report = impact.get_impact_report()
        assert report["total_hours_saved"] > 0
        assert report["hours_saved_value_usd"] > 0

    def test_roi_calculation(self):
        """Test ROI estimation."""
        impact = ImpactMetrics()
        impact.record_episode_impact("email_classify", 0.9, phishing_detected=True)
        impact.record_episode_impact("email_respond", 0.9)

        report = impact.get_impact_report()
        assert report["estimated_total_value_usd"] > 0


class TestExplainabilityReport:
    """Test explainability reporting."""

    def test_log_decision(self):
        """Test decision logging."""
        explainer = ExplainabilityReport()
        explainer.log_decision(
            "ep_1", "email_classify", "Priority: urgent", 0.95, {"phishing_bonus": True}
        )

        decisions = explainer.get_recent_decisions(limit=1)
        assert len(decisions) == 1
        assert decisions[0]["episode_id"] == "ep_1"

    def test_explain_episode(self):
        """Test episode explanation."""
        explainer = ExplainabilityReport()
        explainer.log_decision(
            "ep_1",
            "email_classify",
            "Priority: urgent Category: billing",
            0.95,
            {"criterion": "both correct"},
        )

        explanation = explainer.explain_episode("ep_1")
        assert explanation["episode_id"] == "ep_1"
        assert "why_this_score" in explanation

    def test_explain_not_found(self):
        """Test explanation for non-existent episode."""
        explainer = ExplainabilityReport()
        explanation = explainer.explain_episode("ep_999")
        assert "error" in explanation

    def test_recent_decisions(self):
        """Test retrieving recent decisions."""
        explainer = ExplainabilityReport()
        for i in range(5):
            explainer.log_decision(f"ep_{i}", "email_classify", f"Response {i}", 0.8, {})

        recent = explainer.get_recent_decisions(limit=3)
        assert len(recent) == 3
