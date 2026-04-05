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


class EmailThread(BaseModel):
    id: str
    subject: str
    emails: list[Email]
    contradictions: list[str]
    true_priority: EmailPriority
    expected_action_items: list[str]
    expected_followup: str


class Observation(BaseModel):
    task_id: str
    task_name: str
    difficulty: str
    prompt: str
    email_data: dict[str, Any]
    step: int
    max_steps: int
    context: Optional[str] = None


class Action(BaseModel):
    message: str


class RewardDetail(BaseModel):
    total: float = Field(ge=0.0, le=1.0)
    breakdown: dict[str, float] = {}
    feedback: str = ""
    penalties: list[str] = []
    bonuses: list[str] = []


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
