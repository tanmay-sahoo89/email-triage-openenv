"""Medium task: Draft a professional response to a complaint email."""

import random

from src.data.emails import RESPOND_EMAILS
from src.models import Email, Observation


class EmailRespondTask:
    task_id = "email_respond"
    task_name = "Response Drafting"
    difficulty = "medium"
    max_steps = 1

    def __init__(self, seed: int = 0):
        self._rng = random.Random(seed)
        self._emails = list(RESPOND_EMAILS)
        self._current: Email | None = None
        self._index = 0

    def pick_email(self, index: int | None = None) -> Email:
        if index is not None:
            self._current = self._emails[index % len(self._emails)]
        else:
            self._current = self._emails[self._index % len(self._emails)]
            self._index += 1
        return self._current

    @property
    def current_email(self) -> Email:
        if self._current is None:
            raise RuntimeError("No email selected. Call pick_email() first.")
        return self._current

    def build_observation(self, step: int = 0) -> Observation:
        email = self.current_email
        prompt = (
            "You are a senior customer support agent. Draft a professional, empathetic "
            "response to the following customer complaint email.\n\n"
            f"From: {email.sender}\n"
            f"Subject: {email.subject}\n"
            f"Date: {email.timestamp}\n\n"
            f"{email.body}\n\n"
            "Requirements:\n"
            "- Start with a professional greeting\n"
            "- Acknowledge the customer's frustration\n"
            "- Show empathy and apologize sincerely\n"
            "- Provide a concrete next step or resolution\n"
            "- Keep the tone professional and calm\n"
            "- Response should be 50-300 words\n"
            "- Do NOT use phrases like 'that is not my problem' or 'you are wrong'"
        )
        return Observation(
            task_id=self.task_id,
            task_name=self.task_name,
            difficulty=self.difficulty,
            prompt=prompt,
            email_data=email.model_dump(),
            step=step,
            max_steps=self.max_steps,
        )
