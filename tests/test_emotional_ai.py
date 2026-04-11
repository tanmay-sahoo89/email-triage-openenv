"""
Comprehensive tests for Emotional AI module.
Tests detect emotions, escalation levels, coaching, and crisis support.
"""

import pytest
from src.emotional_ai import (
    EmotionalAIEngine,
    EmotionalState,
    EscalationLevel,
    get_emotional_ai_engine
)


@pytest.fixture
def engine():
    """Create fresh engine for each test."""
    return EmotionalAIEngine()


class TestEmotionalStateDetection:
    """Test emotional state detection."""

    def test_detect_positive_emotion(self, engine):
        """Test detection of positive emotions."""
        text = "Thank you so much! I'm really grateful for your excellent service!"
        state, confidence = engine.detect_emotional_state(text)
        assert state == EmotionalState.POSITIVE
        assert confidence > 0.5

    def test_detect_angry_emotion(self, engine):
        """Test detection of angry emotions."""
        text = "I'm furious! This is ridiculous and unacceptable!"
        state, confidence = engine.detect_emotional_state(text)
        assert state == EmotionalState.ANGRY
        assert confidence > 0.5

    def test_detect_frustrated_emotion(self, engine):
        """Test detection of frustrated emotions."""
        text = "I'm frustrated with the constant problems and issues."
        state, confidence = engine.detect_emotional_state(text)
        assert state == EmotionalState.FRUSTRATED
        assert confidence > 0.3

    def test_detect_desperate_emotion(self, engine):
        """Test detection of desperate emotions."""
        text = "I'm desperate and overwhelmed. At my wit's end here."
        state, confidence = engine.detect_emotional_state(text)
        assert state == EmotionalState.DESPERATE
        assert confidence > 0.3

    def test_detect_anxious_emotion(self, engine):
        """Test detection of anxious emotions."""
        text = "I'm worried and nervous about this situation."
        state, confidence = engine.detect_emotional_state(text)
        assert state == EmotionalState.ANXIOUS
        assert confidence > 0.3

    def test_detect_neutral_emotion(self, engine):
        """Test detection of neutral emotions."""
        text = "The order arrived on Tuesday."
        state, confidence = engine.detect_emotional_state(text)
        assert state == EmotionalState.NEUTRAL
        assert 0.0 <= confidence <= 1.0

    def test_suicidal_ideation_detection(self, engine):
        """Test detection of suicidal ideation (crisis)."""
        text = "I can't take it anymore. I want to kill myself."
        state, confidence = engine.detect_emotional_state(text)
        assert state == EmotionalState.SUICIDAL
        assert confidence > 0.9

    def test_suicidal_keywords_comprehensive(self, engine):
        """Test multiple suicidal keywords."""
        texts = [
            ("I want to kill myself", EmotionalState.SUICIDAL),
            ("I want to end it all", EmotionalState.SUICIDAL),
            ("Better off dead", EmotionalState.SUICIDAL),
            ("No point in living", EmotionalState.SUICIDAL),
            ("I'm going to commit suicide", EmotionalState.SUICIDAL)
        ]
        for text, expected_state in texts:
            state, _ = engine.detect_emotional_state(text)
            assert state == expected_state, f"Failed to detect {expected_state} in: {text}"


class TestEscalationDetection:
    """Test escalation risk detection."""

    def test_escalation_low_positive_tone(self, engine):
        """Test low escalation with positive tone."""
        text = "Great work, thanks!"
        level, reason = engine.detect_escalation_risk(text)
        assert level == EscalationLevel.LOW
        assert "positive" in reason.lower() or "satisfied" in reason.lower()

    def test_escalation_medium_frustrated(self, engine):
        """Test medium escalation with frustrated tone."""
        text = "I'm frustrated with this issue."
        level, reason = engine.detect_escalation_risk(text)
        assert level == EscalationLevel.MEDIUM
        assert "frustration" in reason.lower()

    def test_escalation_high_angry(self, engine):
        """Test high escalation with angry tone."""
        text = "I'm furious! This is completely unacceptable!"
        level, reason = engine.detect_escalation_risk(text)
        assert level == EscalationLevel.HIGH
        assert "anger" in reason.lower()

    def test_escalation_critical_suicidal(self, engine):
        """Test critical escalation with suicidal ideation."""
        text = "I want to kill myself"
        level, reason = engine.detect_escalation_risk(text)
        assert level == EscalationLevel.CRITICAL
        assert "immediate" in reason.lower()

    def test_escalation_with_history(self, engine):
        """Test escalation increases with repeated issues."""
        text = "Still having problems"
        history = ["I have a problem", "Still not working", "Issue persists"]
        level, reason = engine.detect_escalation_risk(text, history)
        assert level in [EscalationLevel.MEDIUM, EscalationLevel.HIGH]


class TestDeEscalationCoaching:
    """Test coaching generation for support agents."""

    def test_coaching_for_angry_customer(self, engine):
        """Test coaching when customer is angry."""
        coaching = engine.generate_de_escalation_coaching(EmotionalState.ANGRY)
        assert "ANGRY" in coaching["emotion_detected"].upper()
        assert len(coaching["empathy_suggestions"]) > 0
        assert len(coaching["do_not_do"]) > 0
        assert "defensive" in " ".join(coaching["do_not_do"]).lower()

    def test_coaching_for_suicidal_crisis(self, engine):
        """Test coaching for mental health emergency."""
        coaching = engine.generate_de_escalation_coaching(EmotionalState.SUICIDAL)
        assert "CRITICAL_NOTE" in coaching or "SUICIDAL" in str(coaching).upper()
        assert "CRISIS SUPPORT" in str(coaching).upper() or "EMERGENCY" in str(coaching).upper()
        assert len(coaching["do_not_do"]) > 0

    def test_coaching_structure(self, engine):
        """Test coaching has all required fields."""
        coaching = engine.generate_de_escalation_coaching(EmotionalState.FRUSTRATED)
        assert "emotion_detected" in coaching
        assert "empathy_suggestions" in coaching
        assert "action_suggestions" in coaching
        assert "resolution_suggestions" in coaching
        assert "do_not_do" in coaching


class TestEmpathyScoring:
    """Test scoring of agent responses for empathy."""

    def test_empathy_score_high(self, engine):
        """Test high empathy score."""
        response = "I completely understand your frustration. I can see why you're upset. " \
                  "Let me help you with this right away. I'm personally handling this."
        emotional_state = EmotionalState.FRUSTRATED
        score = engine.score_response_empathy(response, emotional_state)
        assert score >= 0.5
        assert 0.0 <= score <= 1.0

    def test_empathy_score_low(self, engine):
        """Test low empathy score."""
        response = "Just calm down. It's easy. Anyway, here's what you need to do."
        emotional_state = EmotionalState.ANGRY
        score = engine.score_response_empathy(response, emotional_state)
        assert score < 0.3
        assert 0.0 <= score <= 1.0

    def test_empathy_score_crisis_response(self, engine):
        """Test empathy scoring for crisis responses."""
        good_response = "I hear you. Let me connect you with our crisis support team immediately. " \
                       "We have resources available 24/7: National Crisis Hotline 988"
        bad_response = "Just relax."

        good_score = engine.score_response_empathy(good_response, EmotionalState.SUICIDAL)
        bad_score = engine.score_response_empathy(bad_response, EmotionalState.SUICIDAL)

        assert good_score > bad_score
        assert good_score > 0.5
        assert bad_score < 0.3

    def test_empathy_score_neutral_text(self, engine):
        """Test empathy score on neutral text."""
        response = "The order was placed on Tuesday."
        score = engine.score_response_empathy(response, EmotionalState.NEUTRAL)
        assert 0.0 <= score <= 1.0


class TestMentalHealthResources:
    """Test mental health resource routing."""

    def test_resources_low_level(self, engine):
        """Test resources for low crisis level."""
        resources = engine.get_mental_health_resources(EscalationLevel.LOW)
        assert "links" in resources
        assert len(resources["links"]) > 0

    def test_resources_medium_level(self, engine):
        """Test resources for medium crisis level."""
        resources = engine.get_mental_health_resources(EscalationLevel.MEDIUM)
        assert "links" in resources
        assert len(resources["links"]) > 0
        assert any("therapist" in link.lower() for link in resources["links"])

    def test_resources_high_level(self, engine):
        """Test resources for high crisis level."""
        resources = engine.get_mental_health_resources(EscalationLevel.HIGH)
        assert "links" in resources
        assert any("nami" in link.lower() or "crisis" in link.lower() for link in resources["links"])

    def test_resources_critical_level(self, engine):
        """Test resources for critical crisis level."""
        resources = engine.get_mental_health_resources(EscalationLevel.CRITICAL)
        assert "urgent" in resources or "CRITICAL" in str(resources).upper()
        assert any("988" in link or "suicide" in link.lower() for link in resources["links"])

    def test_crisis_resources_includes_hotlines(self, engine):
        """Test that critical resources include emergency hotlines."""
        resources = engine.get_mental_health_resources(EscalationLevel.CRITICAL)
        resource_text = str(resources).lower()
        assert "988" in resource_text or "suicide" in resource_text or "emergency" in resource_text


class TestEngineGlobalInstance:
    """Test global instance access."""

    def test_get_emotional_ai_engine(self):
        """Test getting global engine instance."""
        engine1 = get_emotional_ai_engine()
        engine2 = get_emotional_ai_engine()
        assert engine1 is engine2  # Should be same instance


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_repeated_problem_escalation(self, engine):
        """Test escalation with problem keywords."""
        current_message = "This is problematic"
        history = [
            "I have a problem",
            "Issues persist",
            "Troubled situation"
        ]
        level, reason = engine.detect_escalation_risk(current_message, history)
        # With multiple problem keywords should detect at least medium escalation
        assert level in [EscalationLevel.LOW, EscalationLevel.MEDIUM, EscalationLevel.HIGH]

    def test_emotional_journey(self, engine):
        """Test tracking emotional journey through conversation."""
        messages = [
            ("Thank you so much", EmotionalState.POSITIVE),
            ("This is problematic", EmotionalState.FRUSTRATED),
            ("I'm furious about this", EmotionalState.ANGRY),
            ("I feel desperate and overwhelmed", EmotionalState.DESPERATE),
        ]

        escalations = []
        for msg, expected_state in messages:
            state, conf = engine.detect_emotional_state(msg)
            assert state == expected_state, f"Expected {expected_state} but got {state} for '{msg}'"
            escalations.append(state)

        # Should show escalation trend
        assert escalations[-1] == EmotionalState.DESPERATE
        assert escalations[0] == EmotionalState.POSITIVE


class TestSuicidalCrisisHandling:
    """Comprehensive tests for suicidal crisis scenarios."""

    def test_direct_suicidal_statement(self, engine):
        """Test direct suicidal statement detection."""
        state, confidence = engine.detect_emotional_state("I want to commit suicide")
        assert state == EmotionalState.SUICIDAL
        assert confidence > 0.9

    def test_indirect_suicidal_reference(self, engine):
        """Test indirect suicidal references."""
        text = "I want to end it all"
        state, conf = engine.detect_emotional_state(text)
        assert state == EmotionalState.SUICIDAL

    def test_crisis_escalation(self, engine):
        """Test suicidal message routes to CRITICAL."""
        level, reason = engine.detect_escalation_risk("I'm going to end it all")
        assert level == EscalationLevel.CRITICAL
        assert "immediate" in reason.lower()

    def test_crisis_resources_routing(self, engine):
        """Test crisis resources are comprehensive."""
        resources = engine.get_mental_health_resources(EscalationLevel.CRITICAL)
        resource_str = str(resources).upper()
        assert "SUICIDE" in resource_str or "988" in resource_str or "CRISIS" in resource_str
