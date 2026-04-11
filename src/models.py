from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class EmailPriority(str, Enum):
    URGENT = "urgent"
    NORMAL = "normal"
    LOW = "low"


class EmailCategory(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    GENERAL = "general"
    COMPLAINT = "complaint"
    SECURITY = "security"
    MEDICAL = "medical"
    LEGAL = "legal"
    HUMANITARIAN = "humanitarian"


class ImpactDomain(str, Enum):
    """Global-impact domains for emails — powers the global-impact scenarios."""
    GENERIC = "generic"
    HEALTHCARE = "healthcare"
    DISASTER_RESPONSE = "disaster_response"
    FINANCIAL_CRIME = "financial_crime"
    HUMANITARIAN = "humanitarian"
    ACCESSIBILITY = "accessibility"
    GDPR = "gdpr"
    CHILD_SAFETY = "child_safety"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    SUPPLY_CHAIN = "supply_chain"


class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str
    priority: EmailPriority
    category: EmailCategory
    is_phishing: bool = False
    emotional_escalation: bool = False
    impact_domain: ImpactDomain = ImpactDomain.GENERIC
    language: str = "en"  # ISO code, supports multilingual scenarios
    headers: dict[str, str] = {}  # simulated email headers for investigation task


class EmailThread(BaseModel):
    id: str
    subject: str
    emails: list[Email]
    contradictions: list[str]
    true_priority: EmailPriority
    expected_action_items: list[str]
    expected_followup: str
    impact_domain: ImpactDomain = ImpactDomain.GENERIC


class InvestigationScenario(BaseModel):
    """A scenario for the email_investigate task — a suspicious email where
    the agent must use tools to gather evidence before deciding."""
    id: str
    email: Email
    ground_truth_verdict: str  # "legitimate" | "suspicious" | "phishing" | "scam" | "bec"
    critical_evidence_tools: list[str]  # tools that should be called to be confident
    red_flags: list[str]  # human-readable red flags
    hidden_knowledge: dict[str, Any]  # what the tools will reveal
    minimum_tools_required: int = 2
    impact_domain: ImpactDomain = ImpactDomain.GENERIC


class WorkflowScenario(BaseModel):
    """A scenario for email_triage_workflow — agent must classify, route,
    draft, and escalate in one episode using multiple actions."""
    id: str
    email: Email
    expected_route: str  # e.g. "billing_team", "security_team", "legal", "eng_oncall"
    expected_sla_hours: int
    expected_escalation: bool
    expected_ticket_severity: str  # "P0" | "P1" | "P2" | "P3"
    expected_reply_keywords: list[str]


class ToolCall(BaseModel):
    """A single tool invocation by the agent."""
    name: str
    arguments: dict[str, Any] = {}


class ToolResult(BaseModel):
    """Result returned to the agent after a tool call."""
    name: str
    ok: bool
    data: dict[str, Any] = {}
    error: Optional[str] = None


class Observation(BaseModel):
    task_id: str
    task_name: str
    difficulty: str
    prompt: str
    email_data: dict[str, Any]
    step: int
    max_steps: int
    context: Optional[str] = None
    hint: Optional[str] = None
    difficulty_mode: str = "normal"  # easy, normal, hard
    # NEW: tools exposed to agent for tool-calling tasks
    available_tools: list[dict[str, Any]] = []
    # NEW: history of previous tool results in this episode (for memory)
    tool_history: list[dict[str, Any]] = []
    # NEW: remaining tool budget (prevents infinite tool spam)
    tool_budget_remaining: int = 0


class Action(BaseModel):
    """Agent action. Can be plain text, a tool call, or both.

    For backward-compat, `message` remains the primary field. New tool-calling
    tasks parse `tool_calls` or fall back to parsing tool invocations out of
    the message string (JSON format: ``TOOL: name({"arg": "val"})``).
    """
    message: str = ""
    tool_calls: list[ToolCall] = []
    # Optional action verb for workflow task: "classify" | "route" | "escalate"
    # | "draft" | "send" | "close" | "final"
    action_type: Optional[str] = None
    payload: dict[str, Any] = {}


class RewardDetail(BaseModel):
    total: float = Field(ge=0.0, le=1.0)
    breakdown: dict[str, float] = {}
    feedback: str = ""
    penalties: list[str] = []
    bonuses: list[str] = []
    ideal_response: Optional[str] = None
    explanations: dict[str, str] = {}
    hints: list[str] = []


class StepResult(BaseModel):
    observation: Observation
    reward: float = Field(ge=0.0, le=1.0)
    done: bool
    info: dict[str, Any] = {}


class State(BaseModel):
    task_id: str
    task_name: str
    difficulty: str
    step: int
    max_steps: int
    done: bool
    total_reward: float
    rewards: list[float]
    metadata: dict[str, Any] = {}
