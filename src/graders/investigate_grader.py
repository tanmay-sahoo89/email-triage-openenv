"""Grader for the email_investigate task.

Rewards:

  1. Verdict correctness (0.50) — was the final verdict right?
  2. Critical-evidence coverage (0.25) — did the agent call the tools that
     would actually reveal ground truth?
  3. Reasoning quality (0.15) — does the justification mention the real
     red flags from the scenario?
  4. Tool efficiency (0.10) — rewards getting to the right answer without
     wasting budget; penalizes both spamming tools and stopping too early.
"""

from __future__ import annotations

import re
from typing import Iterable

from src.models import InvestigationScenario, RewardDetail, ToolCall


VERDICT_ALIASES = {
    "legit": "legitimate",
    "legitimate": "legitimate",
    "valid": "legitimate",
    "safe": "legitimate",
    "suspicious": "suspicious",
    "sus": "suspicious",
    "unclear": "suspicious",
    "phishing": "phishing",
    "phish": "phishing",
    "credential harvest": "phishing",
    "scam": "scam",
    "fraud": "scam",
    "fraudulent": "scam",
    "extortion": "scam",
    "ransom": "scam",
    "bec": "bec",
    "business email compromise": "bec",
    "ceo fraud": "bec",
    "invoice fraud": "bec",
    "impersonation": "bec",
}


def _normalize_verdict(v: str | None) -> str | None:
    if not v:
        return None
    lower = v.lower().strip()
    if lower in VERDICT_ALIASES:
        return VERDICT_ALIASES[lower]
    for alias, canonical in VERDICT_ALIASES.items():
        if alias in lower:
            return canonical
    return None


def _tfidf_overlap(text_a: str, text_b: str) -> float:
    """Simple bag-of-words Jaccard similarity (no external deps)."""
    def tokens(s: str) -> set[str]:
        return set(re.findall(r"\b[a-z]{4,}\b", s.lower()))

    a, b = tokens(text_a), tokens(text_b)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def grade_investigation(
    final_verdict: str | None,
    justification: str,
    tools_called: list[ToolCall],
    scenario: InvestigationScenario,
    reasoning_texts: list[str] | None = None,
) -> RewardDetail:
    """Grade a completed investigation. Returns a RewardDetail in [0.01, 0.99]."""
    penalties: list[str] = []
    bonuses: list[str] = []
    breakdown: dict[str, float] = {}
    explanations: dict[str, str] = {}
    hints: list[str] = []

    reasoning_texts = reasoning_texts or []
    full_reasoning = " ".join(reasoning_texts + [justification or ""]).strip()

    # ── 1. Verdict correctness (0.50) ──────────────────────────────────────
    verdict_norm = _normalize_verdict(final_verdict)
    gt = scenario.ground_truth_verdict
    verdict_score = 0.0
    if verdict_norm == gt:
        verdict_score = 1.0
        bonuses.append("correct_verdict")
        explanations["verdict"] = f"Correct verdict: {gt}"
    elif verdict_norm is None:
        verdict_score = 0.0
        penalties.append("no_verdict_submitted")
        explanations["verdict"] = "No final verdict was submitted"
        hints.append("Always call TOOL: final_verdict(...) at the end of your investigation")
    else:
        # Partial credit for "close enough" categories
        close = {
            ("phishing", "scam"): 0.55,
            ("scam", "phishing"): 0.55,
            ("phishing", "bec"): 0.60,
            ("bec", "phishing"): 0.60,
            ("scam", "bec"): 0.45,
            ("bec", "scam"): 0.45,
            ("suspicious", "phishing"): 0.40,
            ("suspicious", "scam"): 0.40,
            ("suspicious", "bec"): 0.40,
            ("legitimate", "suspicious"): 0.15,
            ("suspicious", "legitimate"): 0.15,
        }
        verdict_score = close.get((verdict_norm, gt), 0.0)
        explanations["verdict"] = (
            f"Submitted '{verdict_norm}' but ground truth is '{gt}'"
            f" (partial credit: {verdict_score:.2f})"
        )
    breakdown["verdict_correctness"] = round(verdict_score, 2)

    # ── 2. Critical-evidence coverage (0.25) ───────────────────────────────
    called_names = {c.name for c in tools_called}
    critical = set(scenario.critical_evidence_tools)
    if critical:
        coverage = len(called_names & critical) / len(critical)
    else:
        coverage = 1.0 if called_names else 0.0
    breakdown["evidence_coverage"] = round(coverage, 2)
    if coverage >= 0.99:
        explanations["evidence"] = f"All critical evidence tools called: {sorted(critical)}"
        bonuses.append("full_evidence_coverage")
    elif coverage >= 0.5:
        missing = sorted(critical - called_names)
        explanations["evidence"] = f"Partial coverage. Missing: {missing}"
        hints.append(f"Call these tools to confirm your verdict: {', '.join(missing)}")
    else:
        explanations["evidence"] = (
            f"Low coverage. Called {sorted(called_names)}, "
            f"but critical tools are {sorted(critical)}"
        )
        hints.append("Focus on tools that actually reveal ground truth: "
                     "domain registration, SPF/DKIM/DMARC, URL reputation.")

    # ── 3. Reasoning quality (0.15) — red flags cited ──────────────────────
    reasoning_score = 0.0
    if scenario.red_flags and full_reasoning:
        cited_flags = 0
        for flag in scenario.red_flags:
            if _tfidf_overlap(full_reasoning, flag) > 0.15:
                cited_flags += 1
        reasoning_score = cited_flags / max(len(scenario.red_flags), 1)
        explanations["reasoning"] = (
            f"Cited {cited_flags}/{len(scenario.red_flags)} red flags in justification"
        )
    elif not scenario.red_flags:
        # Legit scenarios — full credit if a justification was offered
        reasoning_score = 1.0 if full_reasoning else 0.3
        explanations["reasoning"] = "Legitimate scenario — no red flags to cite"
    else:
        explanations["reasoning"] = "No reasoning text provided"
    breakdown["reasoning_quality"] = round(reasoning_score, 2)

    # ── 4. Tool efficiency (0.10) ──────────────────────────────────────────
    n_calls = len(tools_called)
    minimum = scenario.minimum_tools_required
    if n_calls == 0:
        efficiency = 0.0
        penalties.append("no_tools_called")
    elif n_calls < minimum:
        efficiency = 0.4 * (n_calls / max(minimum, 1))
        penalties.append("insufficient_investigation")
    elif n_calls <= minimum + 1:
        efficiency = 1.0
        bonuses.append("efficient_investigation")
    elif n_calls <= minimum + 3:
        efficiency = 0.75
    else:
        efficiency = max(0.2, 0.75 - 0.1 * (n_calls - minimum - 3))
        penalties.append("tool_overuse")
    breakdown["tool_efficiency"] = round(efficiency, 2)

    # ── Combine ────────────────────────────────────────────────────────────
    total = (
        verdict_score * 0.50
        + coverage * 0.25
        + reasoning_score * 0.15
        + efficiency * 0.10
    )

    # Special case: penalize paying-action patterns in justifications
    # (agents shouldn't recommend paying ransoms, etc.)
    bad_recs = ["pay the ransom", "send the bitcoin", "wire the money", "transfer the funds"]
    if any(b in full_reasoning.lower() for b in bad_recs):
        total = max(total - 0.2, 0.01)
        penalties.append("recommended_harmful_action")

    total = round(min(max(total, 0.0), 1.0), 2)

    feedback = (
        f"Verdict: {verdict_norm or 'none'} (truth: {gt}, {verdict_score:.0%}) | "
        f"Evidence: {coverage:.0%} | Reasoning: {reasoning_score:.0%} | "
        f"Tools used: {n_calls}/{scenario.minimum_tools_required}+"
    )

    if total < 0.7 and not hints:
        hints.append(
            "Call critical evidence tools first, then reason from concrete data, "
            "then submit final_verdict with a specific justification."
        )

    return RewardDetail(
        total=total,
        breakdown=breakdown,
        feedback=feedback,
        penalties=penalties,
        bonuses=bonuses,
        ideal_response=(
            f"Correct verdict: {gt}. Key evidence: "
            + "; ".join(scenario.red_flags or ["all authenticity checks pass"])
        ),
        explanations=explanations,
        hints=hints,
    )
