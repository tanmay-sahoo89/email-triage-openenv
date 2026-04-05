"""Hard task: Resolve a multi-email thread with contradictions (multi-turn)."""

import random

from src.data.emails import THREAD_SCENARIOS
from src.models import EmailThread, Observation


STEP_PROMPTS = {
    0: (
        "You are a senior executive assistant. Read the following email thread carefully.\n\n"
        "{thread_text}\n\n"
        "STEP 1 of 4: Identify all contradictions in this thread.\n"
        "List each contradiction clearly, noting which senders disagree and what they claim."
    ),
    1: (
        "Good. Now for STEP 2 of 4:\n"
        "Based on the contradictions you identified, determine the TRUE priority level "
        "for this situation.\n\n"
        "Respond with:\n"
        "Priority: <urgent|normal|low>\n"
        "Justification: <explain why this priority is correct given the contradictions>"
    ),
    2: (
        "STEP 3 of 4: Draft a resolution plan.\n"
        "Provide a clear, actionable resolution that addresses the contradictions. "
        "Include specific action items with owners. List at least 3 concrete action items."
    ),
    3: (
        "STEP 4 of 4: Write a follow-up recommendation.\n"
        "Suggest what follow-up actions or meetings should happen next to ensure "
        "alignment across all stakeholders. Be specific about timing and participants."
    ),
}


class EmailThreadTask:
    task_id = "email_thread"
    task_name = "Thread Resolution"
    difficulty = "hard"
    max_steps = 4

    def __init__(self, seed: int = 0):
        self._rng = random.Random(seed)
        self._threads = list(THREAD_SCENARIOS)
        self._current: EmailThread | None = None
        self._index = 0
        self._agent_responses: list[str] = []

    def pick_email(self, index: int | None = None) -> EmailThread:
        if index is not None:
            self._current = self._threads[index % len(self._threads)]
        else:
            self._current = self._threads[self._index % len(self._threads)]
            self._index += 1
        self._agent_responses = []
        return self._current

    @property
    def current_thread(self) -> EmailThread:
        if self._current is None:
            raise RuntimeError("No thread selected. Call pick_email() first.")
        return self._current

    def record_response(self, response: str) -> None:
        self._agent_responses.append(response)

    @property
    def agent_responses(self) -> list[str]:
        return list(self._agent_responses)

    def _format_thread(self) -> str:
        thread = self.current_thread
        parts = [f"Subject: {thread.subject}\n"]
        for i, email in enumerate(thread.emails, 1):
            parts.append(
                f"--- Email {i} ---\n"
                f"From: {email.sender}\n"
                f"Date: {email.timestamp}\n"
                f"{email.body}\n"
            )
        return "\n".join(parts)

    def build_observation(self, step: int = 0) -> Observation:
        thread = self.current_thread
        thread_text = self._format_thread()

        if step == 0:
            prompt = STEP_PROMPTS[0].format(thread_text=thread_text)
        elif step in STEP_PROMPTS:
            context_parts = [f"Thread subject: {thread.subject}\n"]
            for i, resp in enumerate(self._agent_responses):
                context_parts.append(f"Your step {i + 1} response:\n{resp}\n")
            context = "\n".join(context_parts)
            prompt = STEP_PROMPTS[step]
        else:
            prompt = "Episode complete."

        context = None
        if step > 0 and self._agent_responses:
            context = "\n---\n".join(
                f"Step {i+1} response: {r}" for i, r in enumerate(self._agent_responses)
            )

        return Observation(
            task_id=self.task_id,
            task_name=self.task_name,
            difficulty=self.difficulty,
            prompt=prompt,
            email_data=thread.model_dump(),
            step=step,
            max_steps=self.max_steps,
            context=context,
        )
