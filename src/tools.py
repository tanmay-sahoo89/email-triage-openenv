"""Tool registry for the email investigation / workflow tasks.

These are deterministic, simulated tools the agent can call while working
on an email. Each tool has:

  - A JSON-schema description (for the LLM to understand usage)
  - A handler function that takes the current scenario + arguments and
    returns a ``ToolResult``

The scenario object can carry a ``hidden_knowledge`` dict that the tool
handlers peek into — that's how we simulate "reputation DB", "domain WHOIS",
"threat intel", "customer CRM", etc. without needing real external APIs.

This turns the environment from a one-shot quiz into a true interactive
investigation sandbox — the defining feature of a finals-tier OpenEnv.
"""

from __future__ import annotations

import re
from typing import Any, Callable

from src.models import Email, ToolCall, ToolResult


# ── Tool schema (shown to the agent) ─────────────────────────────────────────

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "lookup_sender_reputation",
        "description": (
            "Query the internal threat-intel database for reputation data on the "
            "sender's email address. Returns reputation score, known-abuser flag, "
            "historical incident count, and first-seen date."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Sender email address"}
            },
            "required": ["email"],
        },
    },
    {
        "name": "check_domain_registration",
        "description": (
            "Check WHOIS/registration data for a domain. Returns registration age "
            "in days, registrar, country, privacy-protected flag, and whether the "
            "domain is on any known-malicious list."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Domain name (e.g. 'example.com')"}
            },
            "required": ["domain"],
        },
    },
    {
        "name": "scan_body_for_iocs",
        "description": (
            "Scan the email body for indicators of compromise (URLs, IP addresses, "
            "cryptocurrency wallets, attachment hashes). Returns a structured list "
            "of IOCs found with risk classifications."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "query_customer_record",
        "description": (
            "Look up an internal customer record by email. Returns account tier, "
            "creation date, open tickets, payment status, and verified-identity flag."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Customer email to look up"}
            },
            "required": ["email"],
        },
    },
    {
        "name": "check_spf_dkim_dmarc",
        "description": (
            "Check authentication results for the email: SPF pass/fail, DKIM "
            "signature validity, DMARC alignment. Critical for detecting spoofing."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "search_past_incidents",
        "description": (
            "Search the incident database for similar past cases. Returns any "
            "previously-logged incidents matching this sender, subject or pattern."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "string",
                    "description": "Space-separated keywords to search",
                }
            },
            "required": ["keywords"],
        },
    },
    {
        "name": "verify_link_safety",
        "description": (
            "Submit a URL to the sandbox URL-reputation service. Returns verdict "
            "(safe/suspicious/malicious), final redirect target, and category."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to check"}
            },
            "required": ["url"],
        },
    },
    {
        "name": "check_internal_directory",
        "description": (
            "Verify whether the sender matches an internal employee directory — "
            "useful for BEC (business email compromise) detection where attackers "
            "impersonate executives."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"],
        },
    },
    {
        "name": "translate_body",
        "description": (
            "Detect language of the email body and translate to English. Returns "
            "detected language code and translated text."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "final_verdict",
        "description": (
            "Submit the final verdict for this investigation. Must be called "
            "exactly once. Verdict must be one of: legitimate, suspicious, "
            "phishing, scam, bec. Include a one-sentence justification."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": ["legitimate", "suspicious", "phishing", "scam", "bec"],
                },
                "justification": {"type": "string"},
            },
            "required": ["verdict", "justification"],
        },
    },
]


# Workflow-task tools (for email_triage_workflow task)
WORKFLOW_TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "classify_email",
        "description": "Assign priority (urgent|normal|low) and category to the email.",
        "parameters": {
            "type": "object",
            "properties": {
                "priority": {"type": "string", "enum": ["urgent", "normal", "low"]},
                "category": {"type": "string"},
            },
            "required": ["priority", "category"],
        },
    },
    {
        "name": "route_to_team",
        "description": (
            "Route the email to the appropriate team. Valid teams: billing_team, "
            "security_team, legal, eng_oncall, support_tier1, support_tier2, exec_escalation, "
            "hr, abuse_desk."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "team": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["team"],
        },
    },
    {
        "name": "set_sla",
        "description": "Set the response SLA in hours for this ticket.",
        "parameters": {
            "type": "object",
            "properties": {
                "hours": {"type": "integer", "minimum": 1, "maximum": 720},
            },
            "required": ["hours"],
        },
    },
    {
        "name": "escalate",
        "description": "Escalate to on-call manager. Use when the issue is P0/P1 or has legal/security implications.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "severity": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]},
            },
            "required": ["reason", "severity"],
        },
    },
    {
        "name": "draft_reply",
        "description": "Draft a reply to the customer. Pass the reply text in 'body'.",
        "parameters": {
            "type": "object",
            "properties": {
                "body": {"type": "string"},
            },
            "required": ["body"],
        },
    },
    {
        "name": "close_ticket",
        "description": "Mark the workflow as complete. Call this only after classifying, routing, and drafting.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]


# ── Tool handlers (scenario-aware) ───────────────────────────────────────────


def _get_domain(email: str) -> str:
    return email.split("@")[-1].lower().strip() if "@" in email else email.strip()


def _handle_lookup_sender_reputation(
    scenario_data: dict[str, Any], email: Email, args: dict[str, Any]
) -> ToolResult:
    target = args.get("email") or email.sender
    kb = scenario_data.get("sender_reputation", {})
    record = kb.get(target.lower())
    if record:
        return ToolResult(name="lookup_sender_reputation", ok=True, data=record)
    # Default: unknown sender
    return ToolResult(
        name="lookup_sender_reputation",
        ok=True,
        data={
            "email": target,
            "reputation": "unknown",
            "score": 50,
            "known_abuser": False,
            "incident_count": 0,
            "first_seen_days_ago": 0,
        },
    )


def _handle_check_domain_registration(
    scenario_data: dict[str, Any], email: Email, args: dict[str, Any]
) -> ToolResult:
    domain = args.get("domain") or _get_domain(email.sender)
    kb = scenario_data.get("domain_whois", {})
    record = kb.get(domain.lower())
    if record:
        return ToolResult(name="check_domain_registration", ok=True, data=record)
    return ToolResult(
        name="check_domain_registration",
        ok=True,
        data={
            "domain": domain,
            "registered_days_ago": 1825,
            "registrar": "GoDaddy",
            "country": "US",
            "privacy_protected": False,
            "malicious_list": False,
        },
    )


def _handle_scan_body_for_iocs(
    scenario_data: dict[str, Any], email: Email, args: dict[str, Any]
) -> ToolResult:
    iocs: dict[str, list[str]] = {
        "urls": re.findall(r"https?://[^\s<>\"']+", email.body),
        "ipv4": re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", email.body),
        "btc_wallets": re.findall(r"\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b", email.body),
        "crypto_generic": re.findall(r"\b0x[a-fA-F0-9]{40}\b", email.body),
    }
    # Scenario can override to inject planted IOCs
    planted = scenario_data.get("planted_iocs", {})
    for k, v in planted.items():
        iocs.setdefault(k, []).extend(v)
    # Risk classification
    risk = "low"
    if iocs["btc_wallets"] or iocs["crypto_generic"]:
        risk = "high"
    elif any("verify" in u.lower() or "secure" in u.lower() for u in iocs["urls"]):
        risk = "medium"
    return ToolResult(
        name="scan_body_for_iocs",
        ok=True,
        data={"iocs": iocs, "risk": risk, "total_found": sum(len(v) for v in iocs.values())},
    )


def _handle_query_customer_record(
    scenario_data: dict[str, Any], email: Email, args: dict[str, Any]
) -> ToolResult:
    target = args.get("email") or email.sender
    kb = scenario_data.get("customer_records", {})
    record = kb.get(target.lower())
    if record:
        return ToolResult(name="query_customer_record", ok=True, data=record)
    return ToolResult(
        name="query_customer_record",
        ok=True,
        data={
            "email": target,
            "account_exists": False,
            "tier": None,
            "open_tickets": 0,
            "payment_status": "n/a",
            "verified_identity": False,
        },
    )


def _handle_check_spf_dkim_dmarc(
    scenario_data: dict[str, Any], email: Email, args: dict[str, Any]
) -> ToolResult:
    kb = scenario_data.get("email_auth", None)
    if kb:
        return ToolResult(name="check_spf_dkim_dmarc", ok=True, data=kb)
    return ToolResult(
        name="check_spf_dkim_dmarc",
        ok=True,
        data={"spf": "pass", "dkim": "pass", "dmarc": "pass", "alignment": True},
    )


def _handle_search_past_incidents(
    scenario_data: dict[str, Any], email: Email, args: dict[str, Any]
) -> ToolResult:
    kw = (args.get("keywords") or "").lower()
    kb = scenario_data.get("past_incidents", [])
    matches = [
        inc for inc in kb
        if any(k in inc.get("summary", "").lower() for k in kw.split())
    ] if kw else kb
    return ToolResult(
        name="search_past_incidents",
        ok=True,
        data={"query": kw, "matches": matches, "count": len(matches)},
    )


def _handle_verify_link_safety(
    scenario_data: dict[str, Any], email: Email, args: dict[str, Any]
) -> ToolResult:
    url = (args.get("url") or "").lower()
    kb = scenario_data.get("url_verdicts", {})
    verdict = kb.get(url, "safe")
    category = "unknown"
    if verdict == "malicious":
        category = "phishing"
    elif verdict == "suspicious":
        category = "typosquat"
    return ToolResult(
        name="verify_link_safety",
        ok=True,
        data={"url": url, "verdict": verdict, "category": category,
              "final_redirect": kb.get(url + ":redirect", url)},
    )


def _handle_check_internal_directory(
    scenario_data: dict[str, Any], email: Email, args: dict[str, Any]
) -> ToolResult:
    name = (args.get("name") or "").lower().strip()
    kb = scenario_data.get("internal_directory", {})
    record = kb.get(name)
    if record:
        return ToolResult(name="check_internal_directory", ok=True, data=record)
    return ToolResult(
        name="check_internal_directory",
        ok=True,
        data={"name": name, "found": False, "match_confidence": 0.0},
    )


def _handle_translate_body(
    scenario_data: dict[str, Any], email: Email, args: dict[str, Any]
) -> ToolResult:
    return ToolResult(
        name="translate_body",
        ok=True,
        data={
            "detected_language": email.language,
            "translated": scenario_data.get("translation", email.body),
        },
    )


HANDLERS: dict[str, Callable[..., ToolResult]] = {
    "lookup_sender_reputation": _handle_lookup_sender_reputation,
    "check_domain_registration": _handle_check_domain_registration,
    "scan_body_for_iocs": _handle_scan_body_for_iocs,
    "query_customer_record": _handle_query_customer_record,
    "check_spf_dkim_dmarc": _handle_check_spf_dkim_dmarc,
    "search_past_incidents": _handle_search_past_incidents,
    "verify_link_safety": _handle_verify_link_safety,
    "check_internal_directory": _handle_check_internal_directory,
    "translate_body": _handle_translate_body,
}


def execute_tool(
    tool_call: ToolCall,
    email: Email,
    scenario_data: dict[str, Any],
) -> ToolResult:
    """Dispatch a tool call to the appropriate handler."""
    handler = HANDLERS.get(tool_call.name)
    if handler is None:
        return ToolResult(
            name=tool_call.name,
            ok=False,
            error=f"unknown_tool: {tool_call.name}",
        )
    try:
        return handler(scenario_data, email, tool_call.arguments or {})
    except Exception as exc:  # pragma: no cover
        return ToolResult(
            name=tool_call.name,
            ok=False,
            error=f"tool_error: {exc}",
        )


# ── Parsing tool calls out of raw LLM output ─────────────────────────────────

_TOOL_LINE_RE = re.compile(
    r"TOOL:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)\s*$",
    re.MULTILINE | re.DOTALL,
)


def parse_tool_calls(text: str) -> list[ToolCall]:
    """Parse tool calls from raw LLM text.

    Supported formats:
      - ``TOOL: name({"arg": "value"})``
      - ``TOOL: name()``
      - Standalone JSON object with ``tool`` and ``arguments`` keys.
    """
    import json

    calls: list[ToolCall] = []

    for match in _TOOL_LINE_RE.finditer(text):
        name = match.group(1).strip()
        raw_args = match.group(2).strip()
        args: dict[str, Any] = {}
        if raw_args:
            try:
                parsed = json.loads(raw_args)
                if isinstance(parsed, dict):
                    args = parsed
            except Exception:
                # Try key=value fallback
                for part in raw_args.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        args[k.strip()] = v.strip().strip('"').strip("'")
        calls.append(ToolCall(name=name, arguments=args))

    # Fallback: standalone JSON object
    if not calls:
        stripped = text.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                obj = json.loads(stripped)
                if isinstance(obj, dict) and "tool" in obj:
                    calls.append(
                        ToolCall(
                            name=obj["tool"],
                            arguments=obj.get("arguments", {}) or {},
                        )
                    )
            except Exception:
                pass

    return calls
