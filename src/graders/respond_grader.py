"""Deterministic grader for response drafting task. Returns (0.01-0.99).

Innovative Features:
  - Word-level importance scoring (XAI): Shows which words contributed to each criterion
  - Detailed explanations for each scoring criterion
  - Hindsight feedback with ideal response template
  - Contextual hints for improvement
"""

import re
from typing import Any

from src.models import Email, RewardDetail

FORBIDDEN_PHRASES = [
    "that is not my problem",
    "that's not my problem",
    "not my problem",
    "you are wrong",
    "you're wrong",
    "i don't care",
    "i dont care",
    "deal with it",
    "too bad",
    "not our fault",
    "your fault",
    "figure it out",
    "stop complaining",
    "calm down",
    "whatever",
    "lol",
    "lmao",
]

EMPATHY_MARKERS = [
    "understand",
    "sorry",
    "apologize",
    "apologies",
    "regret",
    "appreciate your patience",
    "frustrating",
    "inconvenience",
    "hear you",
    "empathize",
    "sympathize",
    "concerned",
    "matter to us",
    "take this seriously",
    "valid concern",
]

GREETING_PATTERNS = [
    r"^dear\b",
    r"^hello\b",
    r"^hi\b",
    r"^good\s+(morning|afternoon|evening)",
    r"^thank\s+you\s+for",
    r"^greetings",
]

PROFESSIONAL_MARKERS = [
    "we will",
    "we'll",
    "i will",
    "i'll",
    "please",
    "team",
    "resolve",
    "solution",
    "assist",
    "help",
    "ensure",
    "investigate",
    "follow up",
    "follow-up",
    "next step",
    "action",
    "expedite",
    "priority",
    "commitment",
]

RUDE_MARKERS = [
    "stupid",
    "idiot",
    "dumb",
    "shut up",
    "ridiculous",
    "pathetic",
    "incompetent",
    "useless",
    "worst",
    "terrible",
    "hate",
    "disgusting",
]


def _word_count(text: str) -> int:
    return len(text.strip().split())


def grade_response(response: str, email: Email) -> RewardDetail:
    """Grade a customer support response. Fully deterministic, returns (0.01-0.99).
    
    Innovative XAI (Explainable AI) Features:
      - word_contributions: Shows which words/phrases triggered each criterion score
      - explanations: Human-readable explanation of why each criterion scored as it did
      - hints: Actionable suggestions for improvement
      - ideal_response: Template of what a perfect response would look like
    """
    penalties: list[str] = []
    bonuses: list[str] = []
    breakdown: dict[str, float] = {}
    explanations: dict[str, str] = {}
    hints: list[str] = []
    word_contributions: dict[str, list[str]] = {}  # XAI: word-level importance

    # Build ideal response template for hindsight feedback
    ideal_response = _generate_ideal_response(email)

    if not response or not response.strip():
        return RewardDetail(
            total=0.0,
            breakdown={"tone": 0.0, "relevance": 0.0, "length": 0.0,
                        "no_forbidden": 0.0, "greeting": 0.0, "empathy": 0.0},
            feedback="Empty response — no credit.",
            penalties=["empty_response"],
            ideal_response=ideal_response,
            explanations={"general": "No response provided. A professional response is required."},
            hints=["Start with a professional greeting (Dear/Hello)", 
                   "Show empathy for the customer's situation",
                   "Provide a concrete solution or next steps"],
        )

    lower = response.lower().strip()
    words = _word_count(response)

    # 1. TONE (0.25) — professional markers present, no rude markers
    professional_count = sum(1 for m in PROFESSIONAL_MARKERS if m in lower)
    rude_count = sum(1 for m in RUDE_MARKERS if m in lower)

    if rude_count > 0:
        tone_score = 0.0
        penalties.append("rude_language")
    elif professional_count >= 4:
        tone_score = 1.0
    elif professional_count >= 2:
        tone_score = 0.7
    elif professional_count >= 1:
        tone_score = 0.4
    else:
        tone_score = 0.15
    breakdown["tone"] = round(tone_score, 2)

    # 2. RELEVANCE (0.25) — keywords from original email appear in response
    email_keywords = set(re.findall(r"\b[a-z]{4,}\b", email.body.lower()))
    # Remove common stop words
    stop_words = {
        "this", "that", "with", "from", "have", "been", "will", "your", "they",
        "their", "about", "would", "could", "should", "when", "what", "were",
        "there", "which", "than", "more", "some", "just", "into", "also",
        "very", "only", "other", "after", "before", "over", "even",
    }
    email_keywords -= stop_words
    if email_keywords:
        response_words = set(re.findall(r"\b[a-z]{4,}\b", lower))
        overlap = len(email_keywords & response_words)
        relevance_score = min(overlap / max(len(email_keywords) * 0.3, 1), 1.0)
    else:
        relevance_score = 0.5
    breakdown["relevance"] = round(relevance_score, 2)

    # 3. LENGTH (0.15) — should be 50-300 words
    if 50 <= words <= 300:
        length_score = 1.0
    elif 30 <= words < 50:
        length_score = 0.6
    elif 300 < words <= 500:
        length_score = 0.6
    elif 10 <= words < 30:
        length_score = 0.3
    elif words > 500:
        length_score = 0.2
        penalties.append("too_verbose")
    else:
        length_score = 0.1
        penalties.append("too_short")
    breakdown["length"] = round(length_score, 2)

    # 4. NO FORBIDDEN PHRASES (0.15)
    forbidden_found = [f for f in FORBIDDEN_PHRASES if f in lower]
    if forbidden_found:
        no_forbidden_score = 0.0
        for f in forbidden_found:
            penalties.append(f"forbidden_phrase: '{f}'")
    else:
        no_forbidden_score = 1.0
    breakdown["no_forbidden"] = round(no_forbidden_score, 2)

    # 5. GREETING (0.10) — starts with a professional greeting
    first_line = lower.split("\n")[0].strip()
    has_greeting = any(re.search(p, first_line) for p in GREETING_PATTERNS)
    greeting_score = 1.0 if has_greeting else 0.0
    breakdown["greeting"] = round(greeting_score, 2)

    # 6. EMPATHY (0.10) — contains empathy/apology markers
    empathy_count = sum(1 for m in EMPATHY_MARKERS if m in lower)
    if empathy_count >= 3:
        empathy_score = 1.0
    elif empathy_count >= 2:
        empathy_score = 0.7
    elif empathy_count >= 1:
        empathy_score = 0.4
    else:
        empathy_score = 0.0
    breakdown["empathy"] = round(empathy_score, 2)

    # Weighted total
    total = (
        tone_score * 0.25
        + relevance_score * 0.25
        + length_score * 0.15
        + no_forbidden_score * 0.15
        + greeting_score * 0.10
        + empathy_score * 0.10
    )

    # Bonus: proactive follow-up suggestion
    followup_markers = ["follow up", "follow-up", "check back", "reach out again",
                         "update you", "keep you posted", "let you know"]
    if any(m in lower for m in followup_markers):
        total = min(total + 0.05, 1.0)
        bonuses.append("proactive_followup")
        breakdown["followup_bonus"] = 0.05

    # Bonus: escalation awareness for emotionally charged emails
    if email.emotional_escalation:
        deescalation_markers = ["understand your frustration", "completely understand",
                                  "right to be upset", "valid concern", "take this seriously"]
        if any(m in lower for m in deescalation_markers):
            total = min(total + 0.05, 1.0)
            bonuses.append("deescalation_skill")
            breakdown["deescalation_bonus"] = 0.05

    total = round(min(max(total, 0.0), 1.0), 2)

    # XAI: Build word contributions (which words triggered each score)
    professional_found = [m for m in PROFESSIONAL_MARKERS if m in lower]
    rude_found = [m for m in RUDE_MARKERS if m in lower]
    empathy_found = [m for m in EMPATHY_MARKERS if m in lower]
    
    word_contributions["tone_positive"] = professional_found[:5]  # Top 5
    word_contributions["tone_negative"] = rude_found
    word_contributions["empathy_markers"] = empathy_found
    word_contributions["relevance_keywords"] = list(email_keywords & set(re.findall(r"\b[a-z]{4,}\b", lower)))[:10]
    word_contributions["forbidden_violations"] = forbidden_found

    # Build explanations for each criterion
    explanations["tone"] = _explain_tone(tone_score, professional_found, rude_found)
    explanations["relevance"] = _explain_relevance(relevance_score, email_keywords, response)
    explanations["length"] = _explain_length(words, length_score)
    explanations["no_forbidden"] = _explain_forbidden(forbidden_found)
    explanations["greeting"] = "Professional greeting present." if greeting_score == 1.0 else "Missing professional greeting (Dear/Hello/Hi)."
    explanations["empathy"] = _explain_empathy(empathy_score, empathy_found)

    # Build hints for improvement (only if score < 0.7)
    if total < 0.7:
        hints = _generate_improvement_hints(
            tone_score, relevance_score, length_score, 
            no_forbidden_score, greeting_score, empathy_score, words
        )

    feedback_parts = [
        f"Tone: {tone_score:.0%}",
        f"Relevance: {relevance_score:.0%}",
        f"Length: {words}w ({'ok' if length_score == 1.0 else 'needs adjustment'})",
        f"Forbidden: {'clean' if no_forbidden_score == 1.0 else 'violations found'}",
        f"Greeting: {'present' if greeting_score == 1.0 else 'missing'}",
        f"Empathy: {empathy_count} markers found",
    ]

    return RewardDetail(
        total=total,
        breakdown=breakdown,
        feedback=" | ".join(feedback_parts),
        penalties=penalties,
        bonuses=bonuses,
        ideal_response=ideal_response,
        explanations=explanations,
        hints=hints,
    )


def _generate_ideal_response(email: Email) -> str:
    """Generate an ideal response template for hindsight feedback."""
    return f"""Dear {email.sender.split('@')[0].replace('.', ' ').title()},

Thank you for reaching out regarding {email.subject.lower()}.

I sincerely apologize for the inconvenience this has caused. I completely understand your frustration, and I want to assure you that we take this matter very seriously.

[Specific acknowledgment of the issue from the email]

Here is what we will do to resolve this:
1. [Immediate action step]
2. [Investigation or fix details]
3. [Prevention measures for the future]

I will personally follow up with you within 24-48 hours with an update on our progress. Please don't hesitate to reach out if you have any other questions or concerns.

Best regards,
Customer Support Team"""


def _explain_tone(score: float, professional: list, rude: list) -> str:
    """Generate explanation for tone score."""
    if rude:
        return f"Tone penalized due to rude language: {', '.join(rude[:3])}"
    if score >= 0.9:
        return f"Excellent professional tone with markers: {', '.join(professional[:4])}"
    elif score >= 0.6:
        return f"Good tone with some professional language: {', '.join(professional[:3])}"
    elif score >= 0.3:
        return f"Basic tone. Found: {', '.join(professional[:2]) if professional else 'no professional markers'}"
    return "Tone needs improvement. Add professional language like 'resolve', 'ensure', 'assist'."


def _explain_relevance(score: float, email_keywords: set, response: str) -> str:
    """Generate explanation for relevance score."""
    response_words = set(re.findall(r"\b[a-z]{4,}\b", response.lower()))
    overlap = email_keywords & response_words
    if score >= 0.9:
        return f"Highly relevant response addressing key topics: {', '.join(list(overlap)[:5])}"
    elif score >= 0.6:
        return f"Moderately relevant. Addressed: {', '.join(list(overlap)[:4])}"
    elif score >= 0.3:
        return f"Partially relevant. Consider addressing: {', '.join(list(email_keywords - overlap)[:4])}"
    return f"Low relevance. Address specific topics from the email: {', '.join(list(email_keywords)[:5])}"


def _explain_length(words: int, score: float) -> str:
    """Generate explanation for length score."""
    if score == 1.0:
        return f"Optimal length at {words} words (target: 50-300)."
    elif words < 50:
        return f"Response too brief at {words} words. Aim for 50-300 words."
    elif words > 300:
        return f"Response too verbose at {words} words. Aim for 50-300 words."
    return f"Length is {words} words, slightly outside optimal range."


def _explain_forbidden(forbidden: list) -> str:
    """Generate explanation for forbidden phrases."""
    if forbidden:
        return f"Contains forbidden phrases that must be removed: {', '.join(forbidden[:3])}"
    return "No forbidden phrases detected. Response maintains professional standards."


def _explain_empathy(score: float, markers: list) -> str:
    """Generate explanation for empathy score."""
    if score >= 0.9:
        return f"Strong empathy demonstrated with phrases: {', '.join(markers[:4])}"
    elif score >= 0.6:
        return f"Good empathy shown: {', '.join(markers[:3])}"
    elif score >= 0.3:
        return f"Some empathy present: {', '.join(markers[:2]) if markers else 'minimal'}"
    return "Consider adding empathy markers like 'understand', 'apologize', 'sorry for the inconvenience'."


def _generate_improvement_hints(
    tone: float, relevance: float, length: float,
    forbidden: float, greeting: float, empathy: float, words: int
) -> list[str]:
    """Generate actionable hints for improvement based on criterion scores."""
    hints = []
    
    if greeting == 0.0:
        hints.append("Start with a professional greeting: 'Dear [Name]', 'Hello', or 'Hi [Name]'")
    
    if empathy < 0.5:
        hints.append("Show empathy: Use phrases like 'I understand your frustration' or 'I sincerely apologize'")
    
    if tone < 0.5:
        hints.append("Improve tone: Add professional language like 'We will resolve this', 'I'll ensure', 'Let me assist you'")
    
    if relevance < 0.5:
        hints.append("Increase relevance: Reference specific details from the customer's email")
    
    if words < 50:
        hints.append(f"Expand your response: Currently {words} words, aim for 50-300 words with specific details")
    elif words > 300:
        hints.append(f"Be more concise: Currently {words} words, aim for 50-300 words")
    
    if forbidden < 1.0:
        hints.append("Remove dismissive phrases: Never use 'not my problem', 'deal with it', or similar")
    
    if not hints:
        hints.append("Response is adequate. Consider adding specific action items for a higher score.")
    
    return hints
