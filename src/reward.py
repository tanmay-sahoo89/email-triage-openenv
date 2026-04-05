"""Reward computation with partial credit, penalties, and bonuses."""

from src.models import RewardDetail


def compute_reward(grader_result: RewardDetail) -> float:
    """Compute final reward from grader output. Returns 0.0-1.0."""
    return grader_result.total


def apply_edge_case_penalties(response: str, base_reward: RewardDetail) -> RewardDetail:
    """Apply additional penalties for adversarial/edge-case responses."""
    penalties = list(base_reward.penalties)
    bonuses = list(base_reward.bonuses)
    total = base_reward.total

    if not response or not response.strip():
        return RewardDetail(
            total=0.0,
            breakdown=base_reward.breakdown,
            feedback="Empty response.",
            penalties=["empty_response"],
            bonuses=[],
        )

    lower = response.lower().strip()

    # Adversarial: response is just repeating the prompt
    if lower.startswith("you are") and len(lower) < 50:
        total = max(total - 0.3, 0.0)
        penalties.append("prompt_repetition")

    # Adversarial: response is all special characters or nonsense
    alpha_ratio = sum(1 for c in response if c.isalpha()) / max(len(response), 1)
    if alpha_ratio < 0.3:
        total = max(total - 0.5, 0.0)
        penalties.append("nonsense_response")

    # Too long: >2000 words is excessive
    word_count = len(response.split())
    if word_count > 2000:
        total = max(total - 0.15, 0.0)
        penalties.append("excessive_length")

    # Single word response
    if word_count <= 1:
        total = max(total * 0.2, 0.0)
        penalties.append("single_word")

    total = round(min(max(total, 0.0), 1.0), 2)

    return RewardDetail(
        total=total,
        breakdown=base_reward.breakdown,
        feedback=base_reward.feedback,
        penalties=penalties,
        bonuses=bonuses,
    )
