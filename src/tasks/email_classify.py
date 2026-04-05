"""Easy task: Classify an email by priority and category."""

import random

from src.data.emails import CLASSIFY_EMAILS
from src.models import Email, Observation


class EmailClassifyTask:
    task_id = "email_classify"
    task_name = "Email Classification"
    difficulty = "easy"
    max_steps = 1

    def __init__(self, seed: int = 0):
        self._rng = random.Random(seed)
        self._emails = list(CLASSIFY_EMAILS)
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
            "You are an email triage assistant. Classify the following email.\n\n"
            f"From: {email.sender}\n"
            f"Subject: {email.subject}\n"
            f"Date: {email.timestamp}\n\n"
            f"{email.body}\n\n"
            "Respond with exactly two lines:\n"
            "Priority: <urgent|normal|low>\n"
            "Category: <billing|technical|general|complaint|security>"
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
