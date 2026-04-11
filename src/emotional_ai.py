"""
Emotional Intelligence & Mental Health Support Module
=====================================================
Detects emotional states, prevents escalations, and routes mental health support.

Global Impact: Reduce escalations by 25%, enable mental health access for underserved populations.
"""

import re
from typing import Dict, List, Tuple
from enum import Enum


class EmotionalState(str, Enum):
    """Emotional states detected in communications."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    DESPERATE = "desperate"
    SUICIDAL = "suicidal_risk"
    ANXIOUS = "anxious"
    SATISFIED = "satisfied"


class EscalationLevel(str, Enum):
    """Escalation risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EmotionalAIEngine:
    """Detect emotions and provide mental health support routing."""

    def __init__(self):
        self.sentiment_keywords = {
            "positive": [
                "thank", "grateful", "appreciate", "excellent", "wonderful",
                "great", "happy", "satisfied", "impressed", "love", "amazing"
            ],
            "frustrated": [
                "frustrated", "annoyed", "upset", "problem", "issue", "trouble",
                "difficulty", "challenge", "struggling", "failed", "terrible", "bad"
            ],
            "angry": [
                "angry", "furious", "outraged", "livid", "hate", "disgusted",
                "unacceptable", "ridiculous", "incompetent", "useless", "worst"
            ],
            "desperate": [
                "desperate", "helpless", "hopeless", "can't take it", "at wit's end",
                "overwhelmed", "breaking down", "losing it", "emergency", "urgent"
            ],
            "anxious": [
                "anxious", "worried", "nervous", "scared", "afraid", "terror",
                "panic", "stressed", "pressure", "hurry", "rush"
            ]
        }

        self.crisis_keywords = [
            "suicide", "self harm", "kill myself", "die", "overdose",
            "cutting", "hang", "jump", "end it all", "don't want to live",
            "better off dead", "no point living", "no point in living", "not worth living"
        ]

        self.de_escalation_phrases = {
            "empathy": [
                "I understand your frustration",
                "I can see why you're upset",
                "Your concern is valid",
                "I appreciate you sharing this"
            ],
            "action": [
                "Here's what we can do",
                "Let me help you with this",
                "I'll take action immediately",
                "Here's my commitment to you"
            ],
            "resolution": [
                "This will be resolved by [date]",
                "You'll see improvement within [timeframe]",
                "I'm personally handling this",
                "You have my word on this"
            ]
        }

    def detect_emotional_state(self, text: str) -> Tuple[EmotionalState, float]:
        """
        Detect emotional state in text.

        Returns:
            (emotional_state, confidence_score)
        """
        text_lower = text.lower()

        # Check for suicidal risk first (highest priority)
        if self._contains_suicidal_keywords(text_lower):
            return EmotionalState.SUICIDAL, 0.95

        # Check other emotional states
        scores = {}
        for emotion, keywords in self.sentiment_keywords.items():
            match_count = sum(1 for kw in keywords if kw in text_lower)
            scores[emotion] = match_count

        if not scores or max(scores.values()) == 0:
            return EmotionalState.NEUTRAL, 0.5

        top_emotion = max(scores, key=scores.get)
        confidence = min(scores[top_emotion] / max(3, max(scores.values())), 1.0)

        emotion_map = {
            "positive": EmotionalState.POSITIVE,
            "frustrated": EmotionalState.FRUSTRATED,
            "angry": EmotionalState.ANGRY,
            "desperate": EmotionalState.DESPERATE,
            "anxious": EmotionalState.ANXIOUS,
        }

        return emotion_map.get(top_emotion, EmotionalState.NEUTRAL), confidence

    def detect_escalation_risk(self, text: str, interaction_history: List[str] = None) -> Tuple[EscalationLevel, str]:
        """
        Detect escalation risk based on text and history.

        Returns:
            (escalation_level, reasoning)
        """
        emotional_state, confidence = self.detect_emotional_state(text)

        # Map emotional states to escalation levels
        state_to_escalation = {
            EmotionalState.SUICIDAL: (EscalationLevel.CRITICAL, "Suicidal ideation detected - IMMEDIATE ACTION REQUIRED"),
            EmotionalState.ANGRY: (EscalationLevel.HIGH, "High anger detected - de-escalation required"),
            EmotionalState.DESPERATE: (EscalationLevel.HIGH, "Desperate tone detected - empathy + action needed"),
            EmotionalState.FRUSTRATED: (EscalationLevel.MEDIUM, "Frustration detected - quick resolution recommended"),
            EmotionalState.ANXIOUS: (EscalationLevel.MEDIUM, "Anxiety detected - reassurance needed"),
            EmotionalState.POSITIVE: (EscalationLevel.LOW, "Positive tone - standard response appropriate"),
            EmotionalState.NEUTRAL: (EscalationLevel.LOW, "Neutral tone - standard response appropriate"),
            EmotionalState.SATISFIED: (EscalationLevel.LOW, "Satisfied customer - maintain satisfaction"),
        }

        level, reasoning = state_to_escalation.get(
            emotional_state,
            (EscalationLevel.MEDIUM, "Unknown emotional state - caution recommended")
        )

        # Check history for repeated failures (increases escalation)
        if interaction_history and len(interaction_history) > 2:
            if all("problem" in msg.lower() for msg in interaction_history[-2:]):
                level = EscalationLevel.HIGH
                reasoning += " | Repeated issue not resolved - escalate immediately"

        return level, reasoning

    def _contains_suicidal_keywords(self, text: str) -> bool:
        """Check if text contains suicidal keywords."""
        return any(kw in text for kw in self.crisis_keywords)

    def generate_de_escalation_coaching(self, emotional_state: EmotionalState) -> Dict[str, str]:
        """
        Generate coaching tips for agent handling distressed customer.

        Returns:
            Coaching with empathy phrases, actions, and resolution commitment
        """
        coaching = {
            "emotion_detected": emotional_state.value,
            "immediate_action": "",
            "empathy_suggestions": self.de_escalation_phrases["empathy"],
            "action_suggestions": self.de_escalation_phrases["action"],
            "resolution_suggestions": self.de_escalation_phrases["resolution"],
            "do_not_do": [],
            "critical_note": ""
        }

        if emotional_state == EmotionalState.SUICIDAL:
            coaching["critical_note"] = "🚨 MENTAL HEALTH EMERGENCY - Contact crisis hotline immediately"
            coaching["immediate_action"] = "TRANSFER TO CRISIS SUPPORT TEAM"
            coaching["do_not_do"] = [
                "Do NOT minimize their feelings",
                "Do NOT tell them to 'calm down'",
                "Do NOT dismiss their concerns",
                "Do NOT delay in getting them help"
            ]

        elif emotional_state == EmotionalState.ANGRY:
            coaching["immediate_action"] = "Listen without interrupting, validate their frustration"
            coaching["do_not_do"] = [
                "Do NOT get defensive",
                "Do NOT argue back",
                "Do NOT blame them"
            ]

        elif emotional_state == EmotionalState.DESPERATE:
            coaching["immediate_action"] = "Show you understand urgency, take immediate action"
            coaching["do_not_do"] = [
                "Do NOT make promises you can't keep",
                "Do NOT delay in acting"
            ]

        return coaching

    def score_response_empathy(self, agent_response: str, emotional_state: EmotionalState) -> float:
        """
        Score how empathetic the agent's response is to the customer's emotional state.

        Returns:
            Empathy score (0.0-1.0)
        """
        response_lower = agent_response.lower()

        # Base empathy components
        empathy_score = 0.0

        # Check for empathy phrases
        empathy_indicators = [
            "understand", "appreciate", "sorry", "feel", "concern", "care",
            "help", "support", "here for you", "grateful", "acknowledge"
        ]
        empathy_count = sum(1 for indicator in empathy_indicators if indicator in response_lower)
        empathy_score += min(empathy_count * 0.15, 0.6)

        # Check for action/solutions
        action_indicators = [
            "do", "will", "here's", "solution", "fix", "resolve", "help",
            "immediately", "right away", "next step"
        ]
        action_count = sum(1 for indicator in action_indicators if indicator in response_lower)
        empathy_score += min(action_count * 0.1, 0.3)

        # Penalize dismissive language
        dismissive_words = ["just", "simply", "easy", "calm down", "relax", "anyway"]
        dismissive_count = sum(1 for word in dismissive_words if word in response_lower)
        empathy_score -= min(dismissive_count * 0.2, 0.5)

        # Bonus for crisis support references (if appropriate)
        if emotional_state == EmotionalState.SUICIDAL:
            if any(ref in response_lower for ref in ["crisis", "hotline", "support", "help"]):
                empathy_score += 0.4
            else:
                empathy_score -= 0.5  # Major penalty for not referencing crisis resources

        return max(0.0, min(empathy_score, 1.0))

    def get_mental_health_resources(self, crisis_level: EscalationLevel) -> Dict:
        """Get mental health resources to route to based on crisis level."""
        resources = {
            "low": {
                "type": "Self-help resources",
                "links": [
                    "https://www.mindful.org/meditation",
                    "https://www.headspace.com",
                    "Local counseling services"
                ]
            },
            "medium": {
                "type": "Professional counseling",
                "links": [
                    "1-800-THERAPIST",
                    "BetterHelp.com",
                    "Local therapist directory"
                ]
            },
            "high": {
                "type": "Urgent mental health support",
                "links": [
                    "NAMI Helpline: 1-800-950-NAMI",
                    "Crisis Text Line: Text HOME to 741741",
                    "Local emergency services"
                ]
            },
            "critical": {
                "type": "🚨 IMMEDIATE CRISIS INTERVENTION 🚨",
                "links": [
                    "🚨 NATIONAL SUICIDE PREVENTION LIFELINE: 988",
                    "🚨 INTERNATIONAL ASSOCIATION FOR SUICIDE PREVENTION: https://www.iasp.info/resources/Crisis_Centres/",
                    "🚨 LOCAL EMERGENCY: 911 (USA) / 999 (UK) / 112 (EU)",
                    "🚨 CRISIS TEXT LINE: Text HOME to 741741"
                ],
                "urgent": "IMMEDIATE professional help required"
            }
        }
        return resources.get(crisis_level.value, resources["low"])


# Global instance
_emotional_engine = EmotionalAIEngine()


def get_emotional_ai_engine() -> EmotionalAIEngine:
    """Get the global emotional AI engine."""
    return _emotional_engine
