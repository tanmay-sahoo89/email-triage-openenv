"""Tests for Multi-Agent Swarm Intelligence."""

import pytest
from src.swarm_intelligence import (
    get_swarm_intelligence,
    MultiAgentSwarm,
    AgentRole,
    Agent,
)


class TestSwarmInitialization:
    """Test swarm creation and agent deployment."""

    def test_swarm_creation(self):
        swarm = get_swarm_intelligence()
        assert swarm is not None
        assert swarm.swarm_size == 6

    def test_agent_initialization(self):
        swarm = get_swarm_intelligence()
        assert len(swarm.agents) == 6
        
        # Check all required roles present
        roles = {agent.role for agent in swarm.agents.values()}
        assert AgentRole.RESEARCH in roles
        assert AgentRole.ANALYSIS in roles
        assert AgentRole.DRAFT in roles
        assert AgentRole.QUALITY in roles
        assert AgentRole.DEBATE in roles
        assert AgentRole.COORDINATION in roles

    def test_agent_specialization(self):
        swarm = get_swarm_intelligence()
        
        for agent in swarm.agents.values():
            assert agent.specialization is not None
            assert len(agent.specialization) > 0
            assert agent.confidence > 0.8


class TestSwarmProcessing:
    """Test email processing through swarm."""

    def test_process_email_swarm(self):
        swarm = get_swarm_intelligence()
        
        email_data = {
            "id": "email_001",
            "subject": "Billing Issue",
            "body": "I was charged twice for my subscription",
            "priority": "urgent",
        }
        
        decision = swarm.process_email_swarm(email_data)
        
        assert decision.decision is not None
        assert decision.confidence > 0.0
        assert decision.consensus_score > 0.0
        assert len(decision.reasoning) > 0
        assert decision.execution_time_ms > 0

    def test_swarm_contributions(self):
        swarm = get_swarm_intelligence()
        
        email_data = {"subject": "Test", "body": "Test email"}
        decision = swarm.process_email_swarm(email_data)
        
        # All agents should contribute
        assert "research" in decision.agent_contributions
        assert "analysis" in decision.agent_contributions
        assert "draft" in decision.agent_contributions
        assert "debate" in decision.agent_contributions
        assert "quality" in decision.agent_contributions

    def test_reasoning_chain(self):
        swarm = get_swarm_intelligence()
        
        email_data = {"subject": "Test", "body": "Test"}
        decision = swarm.process_email_swarm(email_data)
        
        # Reasoning should show agent contributions
        reasoning_str = "\n".join(decision.reasoning)
        assert "Research Agent" in reasoning_str
        assert "Analysis Agent" in reasoning_str
        assert "SWARM SYNTHESIS" in reasoning_str


class TestConsensusCalculation:
    """Test consensus and agreement scoring."""

    def test_consensus_score_calculation(self):
        swarm = get_swarm_intelligence()
        
        email_data = {"subject": "Test", "body": "Test"}
        decision = swarm.process_email_swarm(email_data)
        
        # Consensus should be between 0 and 1
        assert 0.0 <= decision.consensus_score <= 1.0
        assert decision.consensus_score > 0.8  # Should be high agreement

    def test_high_confidence(self):
        swarm = get_swarm_intelligence()
        
        email_data = {"subject": "Test", "body": "Test"}
        decision = swarm.process_email_swarm(email_data)
        
        # Swarm should have high confidence (40-60% improvement over single agent)
        assert decision.confidence > 0.85


class TestPerformanceMetrics:
    """Test performance tracking and metrics."""

    def test_performance_report(self):
        swarm = get_swarm_intelligence()
        
        # Process a few emails
        for i in range(3):
            email_data = {"subject": f"Test {i}", "body": "Test"}
            swarm.process_email_swarm(email_data)
        
        report = swarm.get_performance_report()
        
        assert report["total_decisions_processed"] >= 3
        assert report["average_confidence"] > 0.0
        assert report["average_consensus"] > 0.0
        assert "accuracy_improvement_vs_baseline" in report

    def test_accuracy_improvement(self):
        swarm = get_swarm_intelligence()
        
        email_data = {"subject": "Test", "body": "Test"}
        swarm.process_email_swarm(email_data)
        
        report = swarm.get_performance_report()
        
        # Should show 40-60% improvement vs single agent baseline
        improvement = float(report["accuracy_improvement_vs_baseline"].rstrip("%"))
        assert improvement > 0  # Should be positive improvement

    def test_decision_history(self):
        swarm = get_swarm_intelligence()
        
        # Process several emails
        for i in range(5):
            email_data = {"subject": f"Test {i}", "body": "Test"}
            swarm.process_email_swarm(email_data)
        
        assert len(swarm.decision_history) >= 5


class TestSwarmScaling:
    """Test dynamic swarm scaling."""

    def test_scale_swarm_up(self):
        swarm = MultiAgentSwarm(swarm_size=6)
        
        result = swarm.scale_swarm(12)
        
        assert result["status"] == "scaled"
        assert result["new_size"] == 12
        assert len(swarm.agents) == 12

    def test_scale_swarm_down(self):
        swarm = MultiAgentSwarm(swarm_size=6)
        
        result = swarm.scale_swarm(3)
        
        assert result["status"] == "scaled"
        assert result["new_size"] == 3
        assert len(swarm.agents) == 3

    def test_scale_swarm_bounds(self):
        swarm = MultiAgentSwarm(swarm_size=6)
        
        # Too small
        result = swarm.scale_swarm(1)
        assert "error" in result
        
        # Too large
        result = swarm.scale_swarm(201)
        assert "error" in result
        
        # Valid range
        result = swarm.scale_swarm(100)
        assert result["status"] == "scaled"

    def test_scale_swarm_range(self):
        swarm = MultiAgentSwarm(swarm_size=6)
        
        # Test boundaries of valid range
        for size in [2, 10, 50, 100, 200]:
            result = swarm.scale_swarm(size)
            assert result["status"] == "scaled"
            assert len(swarm.agents) == size


class TestSwarmStatus:
    """Test swarm status reporting."""

    def test_swarm_status(self):
        swarm = get_swarm_intelligence()
        
        status = swarm.get_swarm_status()
        
        assert status["swarm_size"] == 6
        assert len(status["agents"]) == 6
        assert status["system_health"] in ["optimal", "degraded"]
        assert "timestamp" in status

    def test_agent_status_details(self):
        swarm = get_swarm_intelligence()
        
        status = swarm.get_swarm_status()
        
        for agent in status["agents"]:
            assert "id" in agent
            assert "role" in agent
            assert "confidence" in agent
            assert "accuracy_score" in agent
            assert 0.0 <= agent["confidence"] <= 1.0


class TestEmergentIntelligence:
    """Test emergent properties of swarm."""

    def test_collective_decision_better_than_individual(self):
        swarm = get_swarm_intelligence()
        
        email_data = {"subject": "Test", "body": "Test"}
        decision = swarm.process_email_swarm(email_data)
        
        # Swarm confidence should exceed individual agent baseline
        individual_agent_baseline = 0.75
        assert decision.confidence > individual_agent_baseline

    def test_agent_specialization_diversity(self):
        swarm = get_swarm_intelligence()
        
        roles = set()
        for agent in swarm.agents.values():
            roles.add(agent.role)
        
        # Should have diverse roles for emergent behavior
        assert len(roles) == 6  # 6 different roles

    def test_decision_improvement_with_debate(self):
        swarm = get_swarm_intelligence()
        
        email_data = {"subject": "Test", "body": "Test"}
        decision = swarm.process_email_swarm(email_data)
        
        # Debate agent should identify concerns
        assert "debate" in decision.agent_contributions
        debate_result = decision.agent_contributions["debate"]
        assert "concerns" in debate_result


class TestGlobalImpact:
    """Test global impact and scalability."""

    def test_enterprise_scalability(self):
        # Small org: 2 agents
        swarm_small = MultiAgentSwarm(swarm_size=2)
        assert len(swarm_small.agents) == 2
        
        # Medium org: 50 agents
        swarm_medium = MultiAgentSwarm(swarm_size=50)
        assert len(swarm_medium.agents) == 50
        
        # Large enterprise: 200 agents
        swarm_large = MultiAgentSwarm(swarm_size=200)
        assert len(swarm_large.agents) == 200

    def test_performance_scales_with_agents(self):
        swarm = MultiAgentSwarm(swarm_size=6)
        
        email_data = {"subject": "Test", "body": "Test"}
        decision = swarm.process_email_swarm(email_data)
        
        baseline_confidence = decision.confidence
        
        # Scale up
        swarm.scale_swarm(12)
        decision2 = swarm.process_email_swarm(email_data)
        
        # More agents should maintain or improve confidence
        assert decision2.confidence >= baseline_confidence * 0.95


class TestRealWorldScenarios:
    """Test with realistic email scenarios."""

    def test_billing_complaint_processing(self):
        swarm = get_swarm_intelligence()
        
        email_data = {
            "id": "ticket_001",
            "subject": "Unauthorized charge on my account",
            "body": "I was charged $99 for a service I canceled last month. This is the 2nd time this happened!",
            "sender": "angry_customer@example.com",
            "priority": "urgent",
        }
        
        decision = swarm.process_email_swarm(email_data)
        
        assert decision.decision == "process_refund_with_credit"
        assert decision.confidence >= 0.85  # Should be high confidence

    def test_technical_issue_processing(self):
        swarm = get_swarm_intelligence()
        
        email_data = {
            "subject": "API integration failing",
            "body": "Our integration with your API has been down for 3 hours. This is urgent!",
        }
        
        decision = swarm.process_email_swarm(email_data)
        
        assert decision.decision is not None
        assert "immediate" in decision.reasoning[0].lower() or any(
            "immediate" in line.lower() for line in decision.reasoning
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
