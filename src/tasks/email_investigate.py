"""Hard task: Interactive email investigation using tools.

This is the flagship agentic task. The agent receives a suspicious email,
then must call tools (lookup_sender_reputation, check_domain_registration,
scan_body_for_iocs, verify_link_safety, etc.) to gather evidence before
submitting a final verdict.

Key agentic properties:
  - Multi-step episodes (up to 8 steps per investigation)
  - Information-revealing tool calls that change the agent's observation
  - Tool budget (prevents infinite tool spam)
  - Terminal action (``final_verdict``) the agent must call to end the episode
  - Grader rewards: tool efficiency + critical-evidence coverage + verdict
    correctness + reasoning quality
"""

from __future__ import annotations

import random
from typing import Any, Optional

from src.data.investigations import INVESTIGATION_SCENARIOS
from src.models import (
    InvestigationScenario,
    Observation,
    ToolCall,
    ToolResult,
)
from src.tools import TOOL_SCHEMAS, execute_tool


INITIAL_PROMPT = (
    "You are a senior email-security analyst on a SOC team. A user forwarded "
    "the following email for investigation. Your job is to:\n\n"
    "  1. Gather evidence by calling the available tools.\n"
    "  2. Reason about red flags, legitimacy, and impact.\n"
    "  3. Submit a final verdict via the `final_verdict` tool.\n\n"
    "Verdict must be one of: legitimate | suspicious | phishing | scam | bec\n"
    "You have a tool budget of {budget} calls. Choose carefully — favor the "
    "tools most likely to reveal ground truth (domain registration, SPF/DKIM, "
    "URL reputation, sender reputation, internal directory).\n\n"
    "─── EMAIL UNDER INVESTIGATION ───\n"
    "From: {sender}\n"
    "Reply-To: {reply_to}\n"
    "Subject: {subject}\n"
    "Date: {timestamp}\n"
    "Language: {language}\n\n"
    "{body}\n\n"
    "─── HOW TO CALL TOOLS ───\n"
    "Emit a line in this exact format (JSON arguments):\n"
    '  TOOL: tool_name({{"arg": "value"}})\n'
    "Example: TOOL: check_domain_registration({{\"domain\": \"example.com\"}})\n"
    "When ready to conclude, call:\n"
    '  TOOL: final_verdict({{"verdict": "phishing", "justification": "..."}})\n'
    "You may include a short reasoning paragraph before the tool call."
)

FOLLOWUP_PROMPT = (
    "Tool budget remaining: {budget}. Previous tool results are in your "
    "context. Call another tool or submit `final_verdict` when ready.\n\n"
    "Remember:\n"
    "  - Call `final_verdict` exactly once to end the investigation.\n"
    "  - Cite specific evidence (domain age, auth failures, IOC hits, "
    "incident-DB matches) in your justification.\n"
    "  - Avoid redundant tool calls — each call costs one budget."
)


class EmailInvestigateTask:
    task_id = "email_investigate"
    task_name = "Interactive Email Investigation"
    difficulty = "hard"
    max_steps = 8
    initial_tool_budget = 6

    def __init__(self, seed: int = 0):
        self._rng = random.Random(seed)
        self._scenarios = list(INVESTIGATION_SCENARIOS)
        self._current: Optional[InvestigationScenario] = None
        self._index = 0
        self._tools_called: list[ToolCall] = []
        self._tool_results: list[ToolResult] = []
        self._tool_budget: int = self.initial_tool_budget
        self._final_verdict: Optional[str] = None
        self._final_justification: str = ""
        self._reasoning_texts: list[str] = []

    # ── lifecycle ──────────────────────────────────────────────────────────

    def pick_email(self, index: int | None = None) -> InvestigationScenario:
        if index is not None:
            self._current = self._scenarios[index % len(self._scenarios)]
        else:
            self._current = self._scenarios[self._index % len(self._scenarios)]
            self._index += 1
        self._tools_called = []
        self._tool_results = []
        self._tool_budget = self.initial_tool_budget
        self._final_verdict = None
        self._final_justification = ""
        self._reasoning_texts = []
        return self._current

    @property
    def current_scenario(self) -> InvestigationScenario:
        if self._current is None:
            raise RuntimeError("No scenario selected. Call pick_email() first.")
        return self._current

    @property
    def current_email(self):
        """Compat property used by the env to track email IDs."""
        return self.current_scenario.email

    # ── step mechanics ─────────────────────────────────────────────────────

    def record_response(self, response: str) -> None:
        self._reasoning_texts.append(response)

    def apply_tool_calls(self, tool_calls: list[ToolCall]) -> list[ToolResult]:
        """Execute tool calls against the scenario's hidden knowledge.
        Returns the list of results. Also tracks tool-budget consumption
        and detects the terminal `final_verdict` call.
        """
        results: list[ToolResult] = []
        scenario = self.current_scenario

        for call in tool_calls:
            if self._final_verdict is not None:
                # Investigation already terminated
                results.append(
                    ToolResult(
                        name=call.name,
                        ok=False,
                        error="investigation_already_closed",
                    )
                )
                continue

            if call.name == "final_verdict":
                verdict = (call.arguments or {}).get("verdict", "").lower()
                justification = (call.arguments or {}).get("justification", "")
                valid = {"legitimate", "suspicious", "phishing", "scam", "bec"}
                if verdict in valid:
                    self._final_verdict = verdict
                    self._final_justification = justification
                    results.append(
                        ToolResult(
                            name="final_verdict",
                            ok=True,
                            data={
                                "verdict": verdict,
                                "justification": justification,
                                "accepted": True,
                            },
                        )
                    )
                else:
                    results.append(
                        ToolResult(
                            name="final_verdict",
                            ok=False,
                            error=f"invalid_verdict: {verdict}",
                        )
                    )
                continue

            if self._tool_budget <= 0:
                results.append(
                    ToolResult(
                        name=call.name,
                        ok=False,
                        error="tool_budget_exhausted",
                    )
                )
                continue

            result = execute_tool(call, scenario.email, scenario.hidden_knowledge)
            self._tool_budget -= 1
            self._tools_called.append(call)
            self._tool_results.append(result)
            results.append(result)

        return results

    @property
    def final_verdict(self) -> Optional[str]:
        return self._final_verdict

    @property
    def final_justification(self) -> str:
        return self._final_justification

    @property
    def tools_called(self) -> list[ToolCall]:
        return list(self._tools_called)

    @property
    def tool_results(self) -> list[ToolResult]:
        return list(self._tool_results)

    @property
    def reasoning_texts(self) -> list[str]:
        return list(self._reasoning_texts)

    @property
    def is_terminal(self) -> bool:
        return self._final_verdict is not None or self._tool_budget <= 0

    # ── observations ───────────────────────────────────────────────────────

    def build_observation(self, step: int = 0) -> Observation:
        scenario = self.current_scenario
        email = scenario.email

        if step == 0:
            prompt = INITIAL_PROMPT.format(
                budget=self._tool_budget,
                sender=email.sender,
                reply_to=email.headers.get("reply-to", email.sender),
                subject=email.subject,
                timestamp=email.timestamp,
                language=email.language,
                body=email.body,
            )
        else:
            prompt = FOLLOWUP_PROMPT.format(budget=self._tool_budget)

        # Build context — tool history as readable summary
        context_parts = []
        for call, result in zip(self._tools_called, self._tool_results):
            status = "ok" if result.ok else "err"
            args_str = ", ".join(f"{k}={v}" for k, v in (call.arguments or {}).items())
            data_preview = str(result.data)[:500] if result.data else (result.error or "")
            context_parts.append(
                f"[{status}] {call.name}({args_str}) -> {data_preview}"
            )
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
            available_tools=TOOL_SCHEMAS,
            tool_history=[
                {
                    "name": r.name,
                    "ok": r.ok,
                    "data": r.data,
                    "error": r.error,
                }
                for r in self._tool_results
            ],
            tool_budget_remaining=self._tool_budget,
        )
