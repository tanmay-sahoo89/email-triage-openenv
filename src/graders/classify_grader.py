"""Deterministic grader for email classification task. Returns (0.01-0.99)."""

from src.models import Email, EmailPriority, EmailCategory, RewardDetail

PRIORITY_ORDER = [EmailPriority.LOW, EmailPriority.NORMAL, EmailPriority.URGENT]

CATEGORY_ALIASES: dict[str, EmailCategory] = {
    "billing": EmailCategory.BILLING,
    "payment": EmailCategory.BILLING,
    "invoice": EmailCategory.BILLING,
    "charge": EmailCategory.BILLING,
    "refund": EmailCategory.BILLING,
    "technical": EmailCategory.TECHNICAL,
    "tech": EmailCategory.TECHNICAL,
    "bug": EmailCategory.TECHNICAL,
    "error": EmailCategory.TECHNICAL,
    "general": EmailCategory.GENERAL,
    "inquiry": EmailCategory.GENERAL,
    "question": EmailCategory.GENERAL,
    "complaint": EmailCategory.COMPLAINT,
    "issue": EmailCategory.COMPLAINT,
    "security": EmailCategory.SECURITY,
    "phishing": EmailCategory.SECURITY,
    "spam": EmailCategory.SECURITY,
    "fraud": EmailCategory.SECURITY,
}


def _extract_priority(text: str) -> EmailPriority | None:
    lower = text.lower()
    for p in EmailPriority:
        if p.value in lower:
            return p
    if "critical" in lower or "emergency" in lower:
        return EmailPriority.URGENT
    if "medium" in lower or "moderate" in lower:
        return EmailPriority.NORMAL
    return None


def _extract_category(text: str) -> EmailCategory | None:
    lower = text.lower()
    for cat in EmailCategory:
        if cat.value in lower:
            return cat
    for alias, cat in CATEGORY_ALIASES.items():
        if alias in lower:
            return cat
    return None


def grade_classification(response: str, email: Email) -> RewardDetail:
    """Grade an email classification response. Fully deterministic, returns (0.01-0.99)."""
    penalties: list[str] = []
    bonuses: list[str] = []
    breakdown: dict[str, float] = {}
    explanations: dict[str, str] = {}
    hints: list[str] = []

    # Build ideal response for hindsight feedback
    ideal_response = f"Priority: {email.priority.value}\nCategory: {email.category.value}"
    if email.is_phishing:
        ideal_response += "\nNote: This email appears to be a phishing attempt."
    if email.emotional_escalation:
        ideal_response += "\nNote: Customer appears emotionally escalated."

    if not response or not response.strip():
        return RewardDetail(
            total=0.0,
            breakdown={"priority": 0.0, "category": 0.0},
            feedback="Empty response — no credit.",
            penalties=["empty_response"],
            ideal_response=ideal_response,
            explanations={"priority": "No priority detected", "category": "No category detected"},
            hints=["Format your response as:\nPriority: <urgent|normal|low>\nCategory: <billing|technical|general|complaint|security>"],
        )

    if len(response) > 2000:
        penalties.append("response_too_long")

    detected_priority = _extract_priority(response)
    detected_category = _extract_category(response)

    # Priority scoring: exact=1.0, off-by-one=0.5, wrong/missing=0.0
    priority_score = 0.0
    if detected_priority is not None:
        if detected_priority == email.priority:
            priority_score = 1.0
        else:
            idx_detected = PRIORITY_ORDER.index(detected_priority)
            idx_actual = PRIORITY_ORDER.index(email.priority)
            if abs(idx_detected - idx_actual) == 1:
                priority_score = 0.5
    breakdown["priority"] = priority_score

    # Priority explanation
    if priority_score == 1.0:
        explanations["priority"] = f"Correct! '{email.priority.value}' matches exactly."
    elif priority_score == 0.5:
        explanations["priority"] = f"Partial credit: '{detected_priority.value if detected_priority else 'none'}' is off by one level from '{email.priority.value}'."
        hints.append(f"The email urgency indicators suggest '{email.priority.value}' priority.")
    else:
        explanations["priority"] = f"Incorrect: expected '{email.priority.value}', got '{detected_priority.value if detected_priority else 'none'}'."
        hints.append(f"Look for urgency keywords like 'URGENT', 'immediately', or 'asap' for priority detection.")

    # Category scoring: exact=1.0, wrong/missing=0.0
    category_score = 0.0
    if detected_category is not None and detected_category == email.category:
        category_score = 1.0
        explanations["category"] = f"Correct! '{email.category.value}' matches exactly."
    else:
        explanations["category"] = f"Incorrect: expected '{email.category.value}', got '{detected_category.value if detected_category else 'none'}'."
        hints.append(f"Consider the main topic: billing issues, technical problems, or security concerns.")
    breakdown["category"] = category_score

    total = priority_score * 0.5 + category_score * 0.5

    # Bonus: phishing detection
    if email.is_phishing:
        lower = response.lower()
        phishing_keywords = ["phishing", "scam", "fraudulent", "suspicious", "fake"]
        if any(kw in lower for kw in phishing_keywords):
            total = min(total + 0.1, 1.0)
            bonuses.append("phishing_detected")
            breakdown["phishing_bonus"] = 0.1

    # Bonus: emotional escalation detection
    if email.emotional_escalation:
        lower = response.lower()
        escalation_keywords = ["escalat", "angry", "upset", "frustrated", "emotional"]
        if any(kw in lower for kw in escalation_keywords):
            total = min(total + 0.05, 1.0)
            bonuses.append("escalation_noted")
            breakdown["escalation_bonus"] = 0.05

    # Penalty: too long
    if "response_too_long" in penalties:
        total = max(total - 0.1, 0.0)

    total = round(total, 2)

    feedback_parts = []
    feedback_parts.append(
        f"Priority: {'correct' if priority_score == 1.0 else 'partial' if priority_score == 0.5 else 'incorrect'} "
        f"(expected {email.priority.value}, got {detected_priority.value if detected_priority else 'none'})"
    )
    feedback_parts.append(
        f"Category: {'correct' if category_score == 1.0 else 'incorrect'} "
        f"(expected {email.category.value}, got {detected_category.value if detected_category else 'none'})"
    )

    return RewardDetail(
        total=total,
        breakdown=breakdown,
        feedback=" | ".join(feedback_parts),
        penalties=penalties,
        bonuses=bonuses,
        ideal_response=ideal_response,
        explanations=explanations,
        hints=hints if total < 0.7 else [],  # Only show hints if score is low
    )
