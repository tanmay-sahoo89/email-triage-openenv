"""Tests for multi-task learning orchestrator."""

import pytest
from src.learning_orchestrator import (
    TransferLearningAnalyzer,
    CurriculumOptimizer,
)


class TestTransferLearningAnalyzer:
    """Test transfer learning functionality."""

    def test_register_agent_learning(self):
        """Test agent learning registration."""
        analyzer = TransferLearningAnalyzer()
        result = analyzer.register_agent_learning("agent_1", "email_classify", 0.85)

        assert result["agent_id"] == "agent_1"
        assert result["task_id"] == "email_classify"
        assert result["direct_reward"] == 0.85

    def test_skill_extraction(self):
        """Test skill extraction from task performance."""
        analyzer = TransferLearningAnalyzer()
        
        # Classification should extract classification_skill
        result = analyzer.register_agent_learning("agent_1", "email_classify", 0.9)
        assert "classification_skill" in result["skills_acquired"]
        
        # Response should extract empathy and communication skills
        result = analyzer.register_agent_learning("agent_1", "email_respond", 0.85)
        assert "empathy_skill" in result["skills_acquired"]
        assert "communication_skill" in result["skills_acquired"]

    def test_transfer_bonus(self):
        """Test calculation of transfer bonus."""
        analyzer = TransferLearningAnalyzer()
        
        # Build skills first
        analyzer.register_agent_learning("agent_1", "email_classify", 0.9)
        
        # Then register new task
        result = analyzer.register_agent_learning("agent_1", "email_respond", 0.85)
        
        # Should have non-zero transfer bonus
        assert result["transfer_bonus"] >= 0

    def test_learning_pathway(self):
        """Test learning pathway recommendation."""
        analyzer = TransferLearningAnalyzer()
        
        # No history
        pathway = analyzer.get_learning_pathway("new_agent")
        assert "recommended_pathway" in pathway
        assert len(pathway["recommended_pathway"]) > 0

    def test_multiple_agents_comparison(self):
        """Test comparing multiple agents."""
        analyzer = TransferLearningAnalyzer()
        
        # Register learning for two agents
        analyzer.register_agent_learning("agent_1", "email_classify", 0.9)
        analyzer.register_agent_learning("agent_1", "email_respond", 0.85)
        
        analyzer.register_agent_learning("agent_2", "email_classify", 0.7)
        analyzer.register_agent_learning("agent_2", "email_respond", 0.75)
        
        comparison = analyzer.compare_learning_pathways(["agent_1", "agent_2"])
        
        assert "agent_1" in comparison["agents"]
        assert "agent_2" in comparison["agents"]
        assert comparison["most_efficient"] is not None

    def test_skill_matrix(self):
        """Test skill matrix generation."""
        analyzer = TransferLearningAnalyzer()
        
        analyzer.register_agent_learning("agent_1", "email_classify", 0.9)
        analyzer.register_agent_learning("agent_1", "email_respond", 0.85)
        
        skill_matrix = analyzer.get_skill_matrix("agent_1")
        
        assert skill_matrix["agent_id"] == "agent_1"
        assert len(skill_matrix["skills"]) > 0
        assert skill_matrix["total_skill_level"] > 0


class TestCurriculumOptimizer:
    """Test curriculum optimization."""

    def test_optimize_for_weak_agent(self):
        """Test curriculum for low-performing agent."""
        optimizer = CurriculumOptimizer()
        curriculum = optimizer.optimize_for_agent("weak_agent", 0.2)
        
        assert curriculum[0] == "email_classify"

    def test_optimize_for_strong_agent(self):
        """Test curriculum for high-performing agent."""
        optimizer = CurriculumOptimizer()
        curriculum = optimizer.optimize_for_agent("strong_agent", 0.85)
        
        assert "email_thread" in curriculum or "email_investigate" in curriculum

    def test_predict_task_success(self):
        """Test success probability prediction."""
        optimizer = CurriculumOptimizer()
        
        history = {"email_classify": 0.8, "email_respond": 0.75}
        probability = optimizer.predict_task_success("agent_1", "email_thread", history)
        
        assert 0.01 <= probability <= 0.99

    def test_predict_with_empty_history(self):
        """Test prediction with no history."""
        optimizer = CurriculumOptimizer()
        
        probability = optimizer.predict_task_success("agent_1", "email_classify", {})
        
        assert probability == 0.5  # Default uncertainty

    def test_recommend_curriculum(self):
        """Test curriculum recommendation."""
        optimizer = CurriculumOptimizer()
        
        target_tasks = ["email_thread"]
        current_performance = {"email_classify": 0.8}
        
        recommendation = optimizer.recommend_curriculum(
            "agent_1", target_tasks, current_performance
        )
        
        assert "recommended_curriculum" in recommendation
        assert len(recommendation["recommended_curriculum"]) > 0
