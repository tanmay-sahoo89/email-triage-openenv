"""Deterministic grader for thread resolution task (multi-turn). Returns (0.01-0.99)."""

import re

from src.models import EmailThread, EmailPriority, RewardDetail

PRIORITY_ORDER = [EmailPriority.LOW, EmailPriority.NORMAL, EmailPriority.URGENT]


def _extract_priority(text: str) -> EmailPriority | None:
    lower = text.lower()
    for p in EmailPriority:
        if p.value in lower:
            return p
    if "critical" in lower or "emergency" in lower:
        return EmailPriority.URGENT
    return None


def _score_contradiction_detection(response: str, thread: EmailThread) -> float:
    """Score how well the agent identified contradictions. Max 1.0."""
    if not response.strip():
        return 0.0

    lower = response.lower()
    score = 0.0

    # Check for each expected contradiction
    for contradiction in thread.contradictions:
        # Extract key noun phrases from the contradiction description
        contra_words = set(re.findall(r"\b[a-z]{4,}\b", contradiction.lower()))
        stop_words = {
            "this", "that", "with", "from", "have", "been", "will", "your",
            "they", "their", "about", "says", "states", "claims",
        }
        contra_words -= stop_words

        response_words = set(re.findall(r"\b[a-z]{4,}\b", lower))
        overlap = len(contra_words & response_words)
        coverage = overlap / max(len(contra_words) * 0.4, 1)
        score += min(coverage, 1.0)

    score = score / max(len(thread.contradictions), 1)

    # Bonus for using words like "contradiction", "conflict", "disagree", "inconsistent"
    conflict_markers = ["contradict", "conflict", "disagree", "inconsisten",
                         "discrepan", "mismatch", "versus", "however", "but"]
    marker_count = sum(1 for m in conflict_markers if m in lower)
    if marker_count >= 2:
        score = min(score + 0.15, 1.0)
    elif marker_count >= 1:
        score = min(score + 0.08, 1.0)

    return round(min(score, 1.0), 2)


def _score_priority(response: str, thread: EmailThread) -> float:
    """Score priority identification. Max 1.0."""
    if not response.strip():
        return 0.0

    detected = _extract_priority(response)
    if detected is None:
        return 0.0
    if detected == thread.true_priority:
        return 1.0
    idx_d = PRIORITY_ORDER.index(detected)
    idx_t = PRIORITY_ORDER.index(thread.true_priority)
    if abs(idx_d - idx_t) == 1:
        return 0.5
    return 0.0


def _score_resolution(response: str, thread: EmailThread) -> float:
    """Score the resolution plan quality. Max 1.0."""
    if not response.strip():
        return 0.0

    lower = response.lower()

    # Check for action items from expected list
    action_score = 0.0
    for item in thread.expected_action_items:
        item_words = set(re.findall(r"\b[a-z]{4,}\b", item.lower()))
        item_words -= {"should", "with", "that", "this", "from", "need"}
        resp_words = set(re.findall(r"\b[a-z]{4,}\b", lower))
        overlap = len(item_words & resp_words)
        if overlap >= max(len(item_words) * 0.3, 1):
            action_score += 1.0

    action_score = action_score / max(len(thread.expected_action_items), 1)

    # Check for structural quality: numbered/bulleted items
    has_structure = bool(re.search(r"(\d+[\.\)]\s|\-\s|\*\s|•)", response))
    structure_bonus = 0.15 if has_structure else 0.0

    return round(min(action_score + structure_bonus, 1.0), 2)


def _score_action_items(response: str, thread: EmailThread) -> float:
    """Score whether specific action items are listed. Max 1.0."""
    if not response.strip():
        return 0.0

    lower = response.lower()

    # Count items that look like action items
    action_patterns = [
        r"\d+[\.\)]\s",  # numbered list
        r"[\-\*•]\s",    # bulleted list
        r"\baction\b",
        r"\btask\b",
        r"\bstep\b",
    ]

    has_list = bool(re.search(r"(\d+[\.\)]\s.+\n?){2,}", response))
    has_bullets = bool(re.search(r"([\-\*•]\s.+\n?){2,}", response))

    if has_list or has_bullets:
        # Count list items
        items = re.findall(r"(?:\d+[\.\)]\s|[\-\*•]\s)(.+)", response)
        item_count = len(items)
        if item_count >= 4:
            return 1.0
        elif item_count >= 3:
            return 0.8
        elif item_count >= 2:
            return 0.5
        else:
            return 0.3

    # No structured list but mentions action-related content
    action_markers = ["need to", "must", "should", "will", "action", "task",
                       "step", "assign", "responsible", "owner", "deadline"]
    count = sum(1 for m in action_markers if m in lower)
    if count >= 3:
        return 0.5
    elif count >= 1:
        return 0.25
    return 0.1


def _score_followup(response: str, thread: EmailThread) -> float:
    """Score follow-up recommendation quality. Max 1.0."""
    if not response.strip():
        return 0.0

    lower = response.lower()

    score = 0.0

    # Check for follow-up keywords
    followup_markers = ["follow up", "follow-up", "meeting", "call", "sync",
                          "reconvene", "check in", "check-in", "review",
                          "debrief", "update", "revisit"]
    marker_count = sum(1 for m in followup_markers if m in lower)
    if marker_count >= 2:
        score += 0.4
    elif marker_count >= 1:
        score += 0.25

    # Check for timing specificity
    time_markers = ["within", "hours", "days", "week", "tomorrow", "immediately",
                     "asap", "24 hours", "48 hours", "by end of", "next"]
    time_count = sum(1 for m in time_markers if m in lower)
    if time_count >= 2:
        score += 0.3
    elif time_count >= 1:
        score += 0.15

    # Check for participant specificity
    followup_words = set(re.findall(r"\b[a-z]{4,}\b", thread.expected_followup.lower()))
    followup_words -= {"with", "that", "this", "from", "should", "within", "send"}
    resp_words = set(re.findall(r"\b[a-z]{4,}\b", lower))
    overlap = len(followup_words & resp_words)
    if overlap >= max(len(followup_words) * 0.3, 1):
        score += 0.3
    elif overlap >= 1:
        score += 0.1

    return round(min(score, 1.0), 2)


def grade_thread_step(
    step: int,
    response: str,
    thread: EmailThread,
) -> RewardDetail:
    """Grade a single step of the thread resolution task."""
    penalties: list[str] = []
    bonuses: list[str] = []

    if not response or not response.strip():
        step_names = {0: "contradiction", 1: "priority", 2: "resolution", 3: "followup"}
        return RewardDetail(
            total=0.01,  # Use 0.01 instead of 0.0 per hackathon rules
            breakdown={step_names.get(step, "unknown"): 0.0},
            feedback=f"Empty response for step {step + 1}.",
            penalties=["empty_response"],
        )

    if len(response) > 5000:
        penalties.append("response_too_long")

    if step == 0:
        score = _score_contradiction_detection(response, thread)
        breakdown = {"contradiction_detection": score}
        feedback = f"Contradiction detection: {score:.0%}"
    elif step == 1:
        score = _score_priority(response, thread)
        breakdown = {"priority_identification": score}
        feedback = f"Priority: {'correct' if score == 1.0 else 'partial' if score == 0.5 else 'incorrect'}"
    elif step == 2:
        resolution_score = _score_resolution(response, thread)
        action_score = _score_action_items(response, thread)
        score = resolution_score * 0.6 + action_score * 0.4
        breakdown = {"resolution_plan": resolution_score, "action_items": action_score}
        feedback = f"Resolution: {resolution_score:.0%} | Action items: {action_score:.0%}"
    elif step == 3:
        score = _score_followup(response, thread)
        breakdown = {"followup_recommendation": score}
        feedback = f"Follow-up quality: {score:.0%}"
    else:
        score = 0.0
        breakdown = {}
        feedback = "Unknown step."

    if "response_too_long" in penalties:
        score = max(score - 0.1, 0.0)

    score = round(min(max(score, 0.0), 1.0), 2)
    # Ensure score is strictly between 0 and 1 (not 0.0 or 1.0) per hackathon rules
    if score <= 0.0:
        score = 0.01
    elif score >= 1.0:
        score = 0.99

    return RewardDetail(
        total=score,
        breakdown=breakdown,
        feedback=feedback,
        penalties=penalties,
        bonuses=bonuses,
    )


def grade_thread_resolution(
    responses: list[str],
    thread: EmailThread,
) -> RewardDetail:
    """Grade the full multi-turn thread resolution. Weighted combination of all steps."""
    step_weights = {0: 0.30, 1: 0.20, 2: 0.25, 3: 0.15}
    # Remaining 0.10 for action items quality (evaluated in step 2)

    total = 0.0
    breakdown: dict[str, float] = {}
    all_penalties: list[str] = []
    all_bonuses: list[str] = []
    feedback_parts: list[str] = []

    for i, resp in enumerate(responses):
        if i > 3:
            break
        step_result = grade_thread_step(i, resp, thread)
        weight = step_weights.get(i, 0.0)
        total += step_result.total * weight
        for k, v in step_result.breakdown.items():
            breakdown[f"step{i+1}_{k}"] = v
        all_penalties.extend(step_result.penalties)
        all_bonuses.extend(step_result.bonuses)
        feedback_parts.append(f"Step {i+1}: {step_result.feedback}")

    # If fewer than 4 steps provided, remaining steps score 0
    total = round(min(max(total, 0.0), 1.0), 2)
    # Ensure score is strictly between 0 and 1 (not 0.0 or 1.0) per hackathon rules
    if total <= 0.0:
        total = 0.01
    elif total >= 1.0:
        total = 0.99

    return RewardDetail(
        total=total,
        breakdown=breakdown,
        feedback=" | ".join(feedback_parts),
        penalties=all_penalties,
        bonuses=all_bonuses,
    )
