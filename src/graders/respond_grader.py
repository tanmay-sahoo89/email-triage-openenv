"""Deterministic grader for response drafting task. Returns 0.0-1.0."""

import re

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
    """Grade a customer support response. Fully deterministic, returns 0.0-1.0."""
    penalties: list[str] = []
    bonuses: list[str] = []
    breakdown: dict[str, float] = {}

    if not response or not response.strip():
        return RewardDetail(
            total=0.0,
            breakdown={"tone": 0.0, "relevance": 0.0, "length": 0.0,
                        "no_forbidden": 0.0, "greeting": 0.0, "empathy": 0.0},
            feedback="Empty response — no credit.",
            penalties=["empty_response"],
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
    )
