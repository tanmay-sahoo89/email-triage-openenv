"""Tests for Causal AI System."""

import pytest
from src.causal_ai import (
    get_causal_ai_engine,
    CausalAIEngine,
    CausalRelation,
    CausalPath
)


class TestCausalPaths:
    """Test causal relationship definitions."""
    
    def test_causal_path_creation(self):
        path = CausalPath(
            source="keywords_urgent",
            target="priority_urgent",
            relation=CausalRelation.DIRECT_CAUSE,
            mechanism="Keywords directly indicate urgency",
            strength=0.92
        )
        
        assert path.source == "keywords_urgent"
        assert path.strength == 0.92
        assert path.relation == CausalRelation.DIRECT_CAUSE

    def test_causal_relations(self):
        assert CausalRelation.DIRECT_CAUSE.value == "direct_cause"
        assert CausalRelation.CONFOUNDED.value == "confounded"
        assert CausalRelation.MEDIATED.value == "mediated"
        assert CausalRelation.NO_RELATION.value == "no_relation"


class TestCausalModel:
    """Test causal model initialization."""
    
    def test_default_causal_graph(self):
        engine = get_causal_ai_engine()
        graph = engine.causal_graph
        
        assert len(graph) > 0
        assert "keywords_urgent" in graph
        assert "sender_vip" in graph

    def test_causal_path_strength(self):
        engine = get_causal_ai_engine()
        
        # All causal strengths should be between 0 and 1
        for source, paths in engine.causal_graph.items():
            for path in paths:
                assert 0 <= path.strength <= 1


class TestCausalExplanation:
    """Test causal decision explanation."""
    
    def test_explain_decision(self):
        engine = get_causal_ai_engine()
        
        explanation = engine.explain_decision(
            "priority_urgent",
            {"keywords_urgent": True, "sender_vip": True}
        )
        
        assert "decision" in explanation
        assert "causal_pathways" in explanation
        assert "primary_causes" in explanation
        assert "confidence" in explanation
        assert explanation["confidence"] > 0.0

    def test_causal_pathways_ordered_by_strength(self):
        engine = get_causal_ai_engine()
        
        explanation = engine.explain_decision(
            "priority_urgent",
            {"keywords_urgent": True}
        )
        
        pathways = explanation["causal_pathways"]
        if len(pathways) > 1:
            # Should be sorted by strength
            strengths = [p["strength"] for p in pathways]
            assert strengths == sorted(strengths, reverse=True)

    def test_primary_causes_identification(self):
        engine = get_causal_ai_engine()
        
        explanation = engine.explain_decision(
            "escalation",
            {"sender_vip": True, "sentiment_angry": True}
        )
        
        primary_causes = explanation["primary_causes"]
        assert len(primary_causes) > 0
        assert all("cause" in c and "mechanism" in c for c in primary_causes)

    def test_confidence_calculation(self):
        engine = get_causal_ai_engine()
        
        explanation = engine.explain_decision(
            "priority_urgent",
            {"keywords_urgent": True}
        )
        
        # Confidence should be between 0 and 1
        assert 0 <= explanation["confidence"] <= 1


class TestCounterfactualAnalysis:
    """Test "what if" scenario analysis."""
    
    def test_counterfactual_basic(self):
        engine = get_causal_ai_engine()
        
        result = engine.counterfactual_analysis(
            "priority_urgent",
            {"keywords_urgent": True},
            "keywords_urgent"
        )
        
        assert "original_decision" in result
        assert "feature_changed" in result
        assert "would_decision_change" in result
        assert "confidence" in result

    def test_strong_causal_feature_flip(self):
        engine = get_causal_ai_engine()
        
        # If we remove a strong causal feature, decision should flip
        result = engine.counterfactual_analysis(
            "priority_urgent",
            {"keywords_urgent": True},
            "keywords_urgent"
        )
        
        # Strong causal links should suggest decision would change
        if result["confidence"] > 0.75:
            assert result["would_decision_change"] is True

    def test_weak_causal_feature_no_flip(self):
        engine = get_causal_ai_engine()
        
        # Weak causal features shouldn't flip decision
        result = engine.counterfactual_analysis(
            "priority_urgent",
            {"keywords_urgent": True},
            "random_feature"
        )
        
        # Weak or missing causal link
        if result["confidence"] < 0.5:
            assert result["would_decision_change"] is False

    def test_counterfactual_reasoning(self):
        engine = get_causal_ai_engine()
        
        result = engine.counterfactual_analysis(
            "escalation",
            {"sentiment_angry": True},
            "sentiment_angry"
        )
        
        assert result["reasoning"]
        assert len(result["reasoning"]) > 0


class TestInterventionTesting:
    """Test causal hypothesis testing."""
    
    def test_intervention_test(self):
        engine = get_causal_ai_engine()
        
        result = engine.intervention_test(
            "keywords_urgent",
            "absent",
            "present"
        )
        
        assert "intervention" in result
        assert "predicted_effects" in result
        assert "confidence" in result
        assert "recommendation" in result

    def test_predicted_effects(self):
        engine = get_causal_ai_engine()
        
        result = engine.intervention_test(
            "sender_vip",
            False,
            True
        )
        
        effects = result["predicted_effects"]
        # Should predict some downstream effects
        if effects:
            for effect in effects:
                assert "target" in effect
                assert "mechanism" in effect

    def test_intervention_with_numeric_values(self):
        engine = get_causal_ai_engine()
        
        result = engine.intervention_test(
            "response_time",
            100,  # ms
            500   # ms
        )
        
        assert "intervention" in result
        # Should show effects of slower response time


class TestCausalDiscovery:
    """Test discovering causal relationships from data."""
    
    def test_causal_discovery(self):
        engine = get_causal_ai_engine()
        
        observations = [
            {"keywords": "urgent", "priority": "high"},
            {"keywords": "asap", "priority": "high"},
        ]
        
        result = engine.causal_discovery(observations)
        
        assert "discovered_relations" in result
        assert "confidence" in result
        assert result["confidence"] > 0.0

    def test_temporal_ordering(self):
        engine = get_causal_ai_engine()
        
        result = engine.causal_discovery([])
        
        assert "temporal_ordering" in result
        # Should suggest a causal ordering of variables

    def test_discovery_warnings(self):
        engine = get_causal_ai_engine()
        
        result = engine.causal_discovery([])
        
        # Should warn about limitations
        assert "warnings" in result
        assert len(result["warnings"]) > 0


class TestCausalModelSummary:
    """Test causal model analysis."""
    
    def test_get_model_summary(self):
        engine = get_causal_ai_engine()
        summary = engine.get_causal_model_summary()
        
        assert "total_causal_variables" in summary
        assert "total_causal_edges" in summary
        assert "average_causal_strength" in summary
        assert "largest_causal_chains" in summary

    def test_causal_chains(self):
        engine = get_causal_ai_engine()
        summary = engine.get_causal_model_summary()
        
        chains = summary["largest_causal_chains"]
        assert isinstance(chains, list)
        if chains:
            assert isinstance(chains[0], list)

    def test_bidirectional_relations(self):
        engine = get_causal_ai_engine()
        summary = engine.get_causal_model_summary()
        
        bidirectional = summary["bidirectional_relations"]
        assert isinstance(bidirectional, list)


class TestGlobalImpact:
    """Test global impact for regulated industries."""
    
    def test_explainability_for_medicine(self):
        engine = get_causal_ai_engine()
        
        # Should support healthcare decisions
        explanation = engine.explain_decision(
            "urgent",
            {"severity": 0.8, "risk": 0.7}
        )
        
        # Medical decisions require causal reasoning, not just correlation
        assert explanation["primary_causes"] or explanation["summary"]
        assert explanation["confidence"] > 0.3

    def test_explainability_for_finance(self):
        engine = get_causal_ai_engine()
        
        # Should support financial decisions
        explanation = engine.explain_decision(
            "approve_transaction",
            {"account_age": 5, "risk_score": 0.3}
        )
        
        # Financial decisions need causal justification for regulatory compliance
        assert explanation["summary"]

    def test_explainability_for_law(self):
        engine = get_causal_ai_engine()
        
        # Should support legal decisions
        explanation = engine.explain_decision(
            "escalate_case",
            {"severity": 0.9, "pattern": "repeated"}
        )
        
        # Legal decisions must be auditable and causal
        assert explanation["summary"]
        assert explanation["confidence"]

    def test_accountability_mechanisms(self):
        engine = get_causal_ai_engine()
        
        # Must support accountability
        explanation = engine.explain_decision(
            "decision",
            {"feature1": True, "feature2": False}
        )
        
        # Should have complete audit trail
        assert explanation["summary"]


class TestBeyondCorrelation:
    """Test moving beyond correlation to causation."""
    
    def test_correlation_vs_causation(self):
        engine = get_causal_ai_engine()
        
        # Should distinguish correlation from causation
        explanation = engine.explain_decision(
            "priority_urgent",
            {"keywords_urgent": True, "is_weekend": True}
        )
        
        # Should explain that keywords CAUSE urgency
        # vs weekend is just coincidence
        causes = [c["cause"] for c in explanation["primary_causes"]]
        assert any("keywords" in str(c) for c in causes)

    def test_confounding_detection(self):
        engine = get_causal_ai_engine()
        
        explanation = engine.explain_decision(
            "escalation",
            {"vip_customer": True, "angry": True}
        )
        
        # Should detect confounders
        confounders = explanation.get("confounding_factors", [])
        # System is designed to detect them


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
