"""Hard task: End-to-end email triage workflow.

The agent receives a customer email and must perform a full triage:

  1. classify_email(priority, category)
  2. route_to_team(team, reason)
  3. set_sla(hours)
  4. escalate(reason, severity)   — only if warranted
  5. draft_reply(body)
  6. close_ticket()

This task tests agentic decision-making: did the agent pick the right
queue? The right SLA? Did it escalate P0s? Did the reply address the
customer's actual concern?
"""

from __future__ import annotations

import random
from typing import Any, Optional

from src.data.workflows import WORKFLOW_SCENARIOS
from src.models import Observation, ToolCall, ToolResult, WorkflowScenario
from src.tools import WORKFLOW_TOOL_SCHEMAS


INITIAL_PROMPT = (
    "You are an automated triage coordinator for a support platform. You "
    "have received a customer email and must drive it through a complete "
    "triage workflow using the available actions.\n\n"
    "REQUIRED STEPS (call in order):\n"
    "  1. classify_email(priority, category)\n"
    "  2. route_to_team(team, reason)\n"
    "  3. set_sla(hours)\n"
    "  4. escalate(reason, severity)  — ONLY if P0/P1 or legal/security impact\n"
    "  5. draft_reply(body)           — 50-300 words addressing the customer\n"
    "  6. close_ticket()              — call when the workflow is complete\n\n"
    "Use this exact format for each action:\n"
    '  TOOL: classify_email({{"priority": "urgent", "category": "billing"}})\n'
    "\n─── EMAIL ───\n"
    "From: {sender}\n"
    "Subject: {subject}\n"
    "Date: {timestamp}\n\n"
    "{body}\n\n"
    "─── VALID TEAMS ───\n"
    "billing_team, security_team, legal, eng_oncall, support_tier1, "
    "support_tier2, exec_escalation, hr, abuse_desk\n"
)

FOLLOWUP_PROMPT = (
    "Continue the triage workflow. Actions completed so far: {completed}. "
    "Remaining required actions: {remaining}. Call `close_ticket()` when done."
)


class EmailTriageWorkflowTask:
    task_id = "email_triage_workflow"
    task_name = "End-to-End Triage Workflow"
    difficulty = "hard"
    max_steps = 7

    REQUIRED_ACTIONS = ["classify_email", "route_to_team", "set_sla", "draft_reply"]

    def __init__(self, seed: int = 0):
        self._rng = random.Random(seed)
        self._scenarios = list(WORKFLOW_SCENARIOS)
        self._current: Optional[WorkflowScenario] = None
        self._index = 0
        self._actions_taken: list[ToolCall] = []
        self._closed: bool = False
        self._escalated: bool = False
        self._classify_args: dict[str, Any] = {}
        self._route_args: dict[str, Any] = {}
        self._sla_hours: Optional[int] = None
        self._draft_body: str = ""

    # ── lifecycle ──────────────────────────────────────────────────────────

    def pick_email(self, index: int | None = None) -> WorkflowScenario:
        if index is not None:
            self._current = self._scenarios[index % len(self._scenarios)]
        else:
            self._current = self._scenarios[self._index % len(self._scenarios)]
            self._index += 1
        self._actions_taken = []
        self._closed = False
        self._escalated = False
        self._classify_args = {}
        self._route_args = {}
        self._sla_hours = None
        self._draft_body = ""
        return self._current

    @property
    def current_scenario(self) -> WorkflowScenario:
        if self._current is None:
            raise RuntimeError("No scenario selected. Call pick_email() first.")
        return self._current

    @property
    def current_email(self):
        return self.current_scenario.email

    # ── step mechanics ─────────────────────────────────────────────────────

    def record_response(self, response: str) -> None:
        # Workflow task scores from structured actions, not free text
        pass

    def apply_tool_calls(self, tool_calls: list[ToolCall]) -> list[ToolResult]:
        results: list[ToolResult] = []
        for call in tool_calls:
            if self._closed:
                results.append(ToolResult(name=call.name, ok=False, error="ticket_closed"))
                continue

            self._actions_taken.append(call)
            name = call.name
            args = call.arguments or {}

            if name == "classify_email":
                self._classify_args = args
                results.append(ToolResult(name=name, ok=True, data={"classified": args}))
            elif name == "route_to_team":
                self._route_args = args
                results.append(ToolResult(name=name, ok=True, data={"routed_to": args.get("team")}))
            elif name == "set_sla":
                self._sla_hours = args.get("hours")
                results.append(ToolResult(name=name, ok=True, data={"sla_hours": self._sla_hours}))
            elif name == "escalate":
                self._escalated = True
                results.append(ToolResult(name=name, ok=True, data={"escalated": True, **args}))
            elif name == "draft_reply":
                self._draft_body = args.get("body", "")
                results.append(ToolResult(name=name, ok=True, data={"reply_length": len(self._draft_body)}))
            elif name == "close_ticket":
                self._closed = True
                results.append(ToolResult(name=name, ok=True, data={"closed": True}))
            else:
                results.append(ToolResult(name=name, ok=False, error=f"unknown_action: {name}"))

        return results

    @property
    def is_terminal(self) -> bool:
        return self._closed

    @property
    def actions_taken(self) -> list[ToolCall]:
        return list(self._actions_taken)

    @property
    def classify_args(self) -> dict[str, Any]:
        return dict(self._classify_args)

    @property
    def route_args(self) -> dict[str, Any]:
        return dict(self._route_args)

    @property
    def sla_hours(self) -> Optional[int]:
        return self._sla_hours

    @property
    def draft_body(self) -> str:
        return self._draft_body

    @property
    def escalated(self) -> bool:
        return self._escalated

    # ── observations ───────────────────────────────────────────────────────

    def build_observation(self, step: int = 0) -> Observation:
        scenario = self.current_scenario
        email = scenario.email

        if step == 0:
            prompt = INITIAL_PROMPT.format(
                sender=email.sender,
                subject=email.subject,
                timestamp=email.timestamp,
                body=email.body,
            )
        else:
            completed = [c.name for c in self._actions_taken]
            remaining = [a for a in self.REQUIRED_ACTIONS if a not in completed]
            prompt = FOLLOWUP_PROMPT.format(
                completed=", ".join(completed) or "none",
                remaining=", ".join(remaining) or "none — call close_ticket()",
            )

        context_parts = []
        for call in self._actions_taken:
            args_str = ", ".join(f"{k}={v}" for k, v in (call.arguments or {}).items())
            context_parts.append(f"- {call.name}({args_str})")
        context = "\n".join(context_parts) if context_parts else None

        return Observation(
            task_id=self.task_id,
            task_name=self.task_name,
            difficulty=self.difficulty,
            prompt=prompt,
            email_data=email.model_dump(),
            step=step,
            max_steps=self.max_steps,
            context=context,
            available_tools=WORKFLOW_TOOL_SCHEMAS,
            tool_history=[],
            tool_budget_remaining=max(0, self.max_steps - step),
        )
