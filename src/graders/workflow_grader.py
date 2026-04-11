"""Grader for the email_triage_workflow task.

Weights:

  - Classification correctness      : 0.20
  - Routing correctness              : 0.20
  - SLA correctness (tolerance band) : 0.15
  - Escalation correctness           : 0.10
  - Required actions completeness    : 0.15
  - Draft reply quality              : 0.20

Total stays in [0.01, 0.99].
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from src.models import RewardDetail, ToolCall, WorkflowScenario


def _word_count(text: str) -> int:
    return len(text.strip().split())


def grade_workflow(
    actions_taken: list[ToolCall],
    classify_args: dict[str, Any],
    route_args: dict[str, Any],
    sla_hours: int | None,
    escalated: bool,
    draft_body: str,
    closed: bool,
    scenario: WorkflowScenario,
) -> RewardDetail:
    penalties: list[str] = []
    bonuses: list[str] = []
    breakdown: dict[str, float] = {}
    explanations: dict[str, str] = {}
    hints: list[str] = []

    names_called = {a.name for a in actions_taken}

    # 1. Classification correctness
    expected_priority = scenario.email.priority.value
    expected_category = scenario.email.category.value
    got_priority = (classify_args.get("priority") or "").lower()
    got_category = (classify_args.get("category") or "").lower()

    p_ok = got_priority == expected_priority
    c_ok = got_category == expected_category
    classify_score = 0.0
    if p_ok and c_ok:
        classify_score = 1.0
    elif p_ok or c_ok:
        classify_score = 0.5
    breakdown["classification"] = classify_score
    explanations["classification"] = (
        f"expected priority={expected_priority}/category={expected_category}, "
        f"got {got_priority}/{got_category}"
    )

    # 2. Routing correctness
    got_team = (route_args.get("team") or "").lower().strip()
    expected_team = scenario.expected_route
    routing_score = 1.0 if got_team == expected_team else 0.0
    # Close-team partial credit
    close_teams = {
        ("security_team", "exec_escalation"): 0.5,
        ("exec_escalation", "security_team"): 0.5,
        ("support_tier1", "support_tier2"): 0.5,
        ("support_tier2", "support_tier1"): 0.5,
        ("billing_team", "support_tier1"): 0.3,
    }
    if routing_score == 0.0:
        routing_score = close_teams.get((got_team, expected_team), 0.0)
    breakdown["routing"] = round(routing_score, 2)
    explanations["routing"] = f"expected team={expected_team}, got {got_team or 'none'}"

    # 3. SLA correctness (tolerance band)
    sla_score = 0.0
    if sla_hours is not None:
        expected_sla = scenario.expected_sla_hours
        ratio = sla_hours / max(expected_sla, 1)
        if 0.5 <= ratio <= 2.0:
            sla_score = 1.0
        elif 0.25 <= ratio <= 4.0:
            sla_score = 0.5
        else:
            sla_score = 0.2
    breakdown["sla"] = round(sla_score, 2)
    explanations["sla"] = (
        f"expected SLA ~{scenario.expected_sla_hours}h, "
        f"got {sla_hours if sla_hours is not None else 'none'}"
    )

    # 4. Escalation correctness
    escalation_score = 0.0
    if scenario.expected_escalation == escalated:
        escalation_score = 1.0
    elif scenario.expected_escalation and not escalated:
        escalation_score = 0.0
        penalties.append("missing_escalation")
    else:
        escalation_score = 0.5
        penalties.append("unnecessary_escalation")
    breakdown["escalation"] = round(escalation_score, 2)
    explanations["escalation"] = (
        f"expected escalate={scenario.expected_escalation}, got {escalated}"
    )

    # 5. Required-actions completeness
    required = {"classify_email", "route_to_team", "set_sla", "draft_reply"}
    completed = len(required & names_called) / len(required)
    breakdown["completeness"] = round(completed, 2)
    explanations["completeness"] = (
        f"called {sorted(required & names_called)}"
    )
    if not closed:
        penalties.append("did_not_close_ticket")

    # 6. Draft reply quality
    draft_score = 0.0
    if draft_body:
        words = _word_count(draft_body)
        length_ok = 30 <= words <= 400
        # keyword coverage
        lower = draft_body.lower()
        kw_hits = sum(1 for k in scenario.expected_reply_keywords if k.lower() in lower)
        kw_ratio = kw_hits / max(len(scenario.expected_reply_keywords), 1)
        length_score = 1.0 if length_ok else 0.4
        draft_score = 0.4 * length_score + 0.6 * kw_ratio
        # Penalize forbidden tone
        forbidden = ["not my problem", "deal with it", "calm down", "whatever"]
        if any(f in lower for f in forbidden):
            draft_score = max(draft_score - 0.3, 0.0)
            penalties.append("rude_draft")
        explanations["draft"] = (
            f"{words} words, matched {kw_hits}/{len(scenario.expected_reply_keywords)} keywords"
        )
    else:
        explanations["draft"] = "No reply drafted"
    breakdown["draft"] = round(draft_score, 2)

    # Combine
    total = (
        0.20 * classify_score
        + 0.20 * routing_score
        + 0.15 * sla_score
        + 0.10 * escalation_score
        + 0.15 * completed
        + 0.20 * draft_score
    )

    if closed and completed >= 0.75:
        bonuses.append("workflow_closed_cleanly")
    if not closed:
        total = max(total - 0.05, 0.0)

    total = round(min(max(total, 0.0), 1.0), 2)

    if total < 0.7:
        if classify_score < 1.0:
            hints.append(
                "Classify with the correct priority + category before routing."
            )
        if routing_score < 1.0:
            hints.append(
                f"Route to '{expected_team}' for this type of email."
            )
        if sla_score < 1.0:
            hints.append(
                f"SLA should be ~{scenario.expected_sla_hours}h for this severity."
            )
        if escalation_score < 1.0 and scenario.expected_escalation:
            hints.append("Escalate P0/P1 issues with legal/security impact.")

    return RewardDetail(
        total=total,
        breakdown=breakdown,
        feedback=(
            f"Classify {classify_score:.0%} | Route {routing_score:.0%} | "
            f"SLA {sla_score:.0%} | Esc {escalation_score:.0%} | "
            f"Complete {completed:.0%} | Draft {draft_score:.0%}"
        ),
        penalties=penalties,
        bonuses=bonuses,
        ideal_response=(
            f"classify_email(priority={expected_priority}, category={expected_category}); "
            f"route_to_team(team={scenario.expected_route}); "
            f"set_sla(hours={scenario.expected_sla_hours}); "
            + ("escalate(...); " if scenario.expected_escalation else "")
            + "draft_reply(...); close_ticket();"
        ),
        explanations=explanations,
        hints=hints,
    )
