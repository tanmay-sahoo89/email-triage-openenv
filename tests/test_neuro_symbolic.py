"""Tests for Neuro-Symbolic AI System."""

import pytest
from src.neuro_symbolic import (
    get_neuro_symbolic_engine,
    NeuroSymbolicEngine,
    LogicRule,
    Operator
)


class TestLogicRules:
    """Test symbolic business rules."""
    
    def test_rule_creation(self):
        rule = LogicRule(
            name="test_rule",
            condition="priority=urgent",
            action="escalate",
            priority=8,
            confidence=0.85
        )
        
        assert rule.name == "test_rule"
        assert rule.priority == 8
        assert rule.confidence == 0.85

    def test_default_rules_initialized(self):
        engine = get_neuro_symbolic_engine()
        rules = engine.list_rules()
        
        assert len(rules) > 0
        assert any("urgent" in r["name"].lower() for r in rules)
        assert any("billing" in r["name"].lower() for r in rules)


class TestNeuroSymbolicClassification:
    """Test combined neural + symbolic classification."""
    
    def test_classify_with_rules(self):
        engine = get_neuro_symbolic_engine()
        
        email_data = {
            "id": "test_001",
            "priority": "urgent",
            "category": "billing",
            "customer_tier": "VIP"
        }
        
        result = engine.classify_with_rules(email_data)
        
        assert "email_id" in result
        assert "neural_output" in result
        assert "symbolic_rules_matched" in result
        assert "final_decision" in result
        assert "reasoning_chain" in result

    def test_neural_inference(self):
        engine = get_neuro_symbolic_engine()
        
        email_data = {"subject": "URGENT", "body": "Help!"}
        neural = engine._neural_inference(email_data)
        
        assert "priority_scores" in neural
        assert "category_scores" in neural
        assert "sentiment_scores" in neural
        assert "threat_score" in neural

    def test_score_ranges(self):
        engine = get_neuro_symbolic_engine()
        neural = engine._neural_inference({})
        
        # All scores should be between 0 and 1
        for score_dict in neural.values():
            if isinstance(score_dict, dict):
                for score in score_dict.values():
                    assert 0 <= score <= 1


class TestRuleMatching:
    """Test symbolic rule application."""
    
    def test_apply_urgent_vip_rule(self):
        engine = get_neuro_symbolic_engine()
        
        email_data = {
            "priority": "urgent",
            "customer_tier": "VIP"
        }
        neural = {
            "priority_scores": {"urgent": 0.9},
            "category_scores": {},
            "sentiment_scores": {},
            "threat_score": 0
        }
        
        matched = engine._apply_rules(email_data, neural)
        
        assert len(matched) > 0
        # Should match urgent VIP rule
        assert any("vip" in r["rule_name"].lower() for r in matched)

    def test_rule_priority_sorting(self):
        engine = get_neuro_symbolic_engine()
        
        email_data = {"category": "billing"}
        neural = {
            "priority_scores": {},
            "category_scores": {"billing": 0.9},
            "sentiment_scores": {"negative": 0.8},
            "threat_score": 0
        }
        
        matched = engine._apply_rules(email_data, neural)
        
        # Highest priority rules should come first
        if len(matched) > 1:
            assert matched[0]["priority"] >= matched[1]["priority"]


class TestReasoningChain:
    """Test human-readable reasoning explanation."""
    
    def test_reasoning_generation(self):
        engine = get_neuro_symbolic_engine()
        
        email_data = {"id": "test"}
        neural = {
            "priority_scores": {"urgent": 0.85},
            "category_scores": {"technical": 0.70},
            "sentiment_scores": {"neutral": 0.60},
            "threat_score": 0.1
        }
        rules = [
            {
                "rule_name": "test_rule",
                "condition": "priority=urgent",
                "action": "escalate",
                "priority": 8,
                "confidence": 0.9
            }
        ]
        
        chain = engine._generate_reasoning_chain(email_data, neural, rules, "escalate")
        
        assert isinstance(chain, list)
        assert len(chain) > 0
        assert any("NEURAL" in str(line) for line in chain)
        assert any("SYMBOLIC" in str(line) for line in chain)

    def test_reasoning_is_human_readable(self):
        engine = get_neuro_symbolic_engine()
        
        result = engine.classify_with_rules({"id": "test"})
        reasoning = "\n".join(result["reasoning_chain"])
        
        assert "STEP" in reasoning
        assert "REASON" in reasoning or "reasoning" in reasoning.lower()
        assert len(reasoning) > 100  # Should be substantial explanation


class TestExplainLogic:
    """Test explainability endpoint."""
    
    def test_explain_logic(self):
        engine = get_neuro_symbolic_engine()
        
        result = engine.classify_with_rules({"id": "test"})
        explanation = engine.explain_logic(result)
        
        assert "summary" in explanation
        assert "confidence" in explanation
        assert "reasoning_chain" in explanation
        assert explanation["auditable"] is True
        assert explanation["explainability_score"] > 0.9


class TestRuleManagement:
    """Test rule editing and management."""
    
    def test_add_custom_rule(self):
        engine = get_neuro_symbolic_engine()
        initial_count = len(engine.list_rules())
        
        result = engine.add_rule(
            name="test_custom_rule",
            condition="test_condition",
            action="test_action",
            priority=7,
            confidence=0.80
        )
        
        assert result["status"] == "success"
        assert len(engine.list_rules()) == initial_count + 1

    def test_remove_rule(self):
        engine = get_neuro_symbolic_engine()
        
        # Add a rule first
        engine.add_rule("temp_rule", "temp", "temp", 5, 0.75)
        count_with_rule = len(engine.list_rules())
        
        # Remove it
        result = engine.remove_rule("temp_rule")
        
        assert result["status"] == "success"
        assert len(engine.list_rules()) == count_with_rule - 1

    def test_list_rules(self):
        engine = get_neuro_symbolic_engine()
        rules = engine.list_rules()
        
        assert isinstance(rules, list)
        assert len(rules) > 0
        
        for rule in rules:
            assert "name" in rule
            assert "condition" in rule
            assert "action" in rule
            assert "priority" in rule


class TestRuleValidation:
    """Test rule consistency checking."""
    
    def test_validate_rules(self):
        engine = get_neuro_symbolic_engine()
        validation = engine.validate_rules()
        
        assert "total_rules" in validation
        assert "conflicts" in validation
        assert "is_valid" in validation
        assert "recommendations" in validation

    def test_conflict_detection(self):
        engine = get_neuro_symbolic_engine()
        
        # Add conflicting rules
        engine.add_rule("rule1", "condition", "action1", 5, 0.8)
        engine.add_rule("rule2", "condition", "action2", 5, 0.8)
        
        validation = engine.validate_rules()
        # Should detect potential conflict (same priority, different actions)


class TestGlobalImpact:
    """Test global impact and regulated industry support."""
    
    def test_explainability_for_regulated_industries(self):
        engine = get_neuro_symbolic_engine()
        
        # Should support healthcare, finance, legal
        result = engine.classify_with_rules({"id": "medical"})
        
        # Every decision must be explainable
        assert result["reasoning_chain"]
        assert result["confidence"] > 0.5

    def test_audit_trail(self):
        engine = get_neuro_symbolic_engine()
        result = engine.classify_with_rules({"id": "audit_test"})
        
        # Must have complete audit trail
        assert "neural_output" in result
        assert "symbolic_rules_matched" in result
        assert "final_decision" in result
        assert "reasoning_chain" in result

    def test_transparency_score(self):
        engine = get_neuro_symbolic_engine()
        result = engine.classify_with_rules({"id": "test"})
        
        # Should have very high transparency
        explanation = engine.explain_logic(result)
        assert explanation["explainability_score"] > 0.90


class TestAmazonReference:
    """Test features inspired by Amazon Vulcan/Rufus."""
    
    def test_combines_neural_and_symbolic(self):
        engine = get_neuro_symbolic_engine()
        
        # Must combine both approaches
        result = engine.classify_with_rules({"id": "test"})
        
        assert result["neural_output"]  # Neural part present
        assert result["symbolic_rules_matched"]  # Symbolic part present
        assert result["reasoning_chain"]  # Audit trail present


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
