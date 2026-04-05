"""Tests for all three graders — deterministic and reproducible."""

import pytest
from src.graders.classify_grader import grade_classification
from src.graders.respond_grader import grade_response
from src.graders.thread_grader import grade_thread_step, grade_thread_resolution
from src.data.emails import CLASSIFY_EMAILS, RESPOND_EMAILS, THREAD_SCENARIOS
from src.models import EmailPriority, EmailCategory


# ── Classification Grader ─────────────────────────────────────────────────────

class TestClassifyGrader:
    def test_perfect_score(self):
        email = CLASSIFY_EMAILS[0]  # urgent billing
        result = grade_classification("Priority: urgent\nCategory: billing", email)
        assert result.total == 1.0

    def test_partial_priority(self):
        email = CLASSIFY_EMAILS[0]  # urgent billing
        result = grade_classification("Priority: normal\nCategory: billing", email)
        assert result.total == 0.75  # 0.5*0.5 + 1.0*0.5

    def test_wrong_everything(self):
        email = CLASSIFY_EMAILS[0]  # urgent billing
        result = grade_classification("Priority: low\nCategory: general", email)
        assert result.total == 0.0

    def test_empty_response(self):
        email = CLASSIFY_EMAILS[0]
        result = grade_classification("", email)
        assert result.total == 0.0
        assert "empty_response" in result.penalties

    def test_phishing_bonus(self):
        email = CLASSIFY_EMAILS[7]  # phishing email c08
        result = grade_classification(
            "Priority: low\nCategory: security\nThis looks like a phishing attempt.", email
        )
        assert result.total >= 1.0
        assert "phishing_detected" in result.bonuses

    def test_deterministic(self):
        email = CLASSIFY_EMAILS[3]
        r1 = grade_classification("Priority: normal\nCategory: billing", email)
        r2 = grade_classification("Priority: normal\nCategory: billing", email)
        assert r1.total == r2.total
        assert r1.breakdown == r2.breakdown

    def test_category_alias(self):
        email = CLASSIFY_EMAILS[0]  # billing
        result = grade_classification("Priority: urgent\nCategory: payment", email)
        assert result.breakdown["category"] == 1.0

    def test_scores_in_range(self):
        for email in CLASSIFY_EMAILS:
            for response in ["", "random text", "Priority: urgent\nCategory: billing",
                              "Priority: low\nCategory: security"]:
                result = grade_classification(response, email)
                assert 0.0 <= result.total <= 1.0


# ── Response Grader ───────────────────────────────────────────────────────────

class TestRespondGrader:
    def test_good_response(self):
        email = RESPOND_EMAILS[0]  # refund complaint
        response = (
            "Dear Customer,\n\n"
            "Thank you for reaching out. I sincerely apologize for the delay with your "
            "refund of $199.99 (ticket #RF-4421). I completely understand your frustration — "
            "waiting three weeks is unacceptable and not the experience we want for you.\n\n"
            "I will personally escalate this to our billing team and ensure your refund is "
            "processed within the next 24 hours. I'll follow up with a confirmation email "
            "once the refund has been issued.\n\n"
            "We take this seriously and appreciate your patience.\n\n"
            "Best regards,\nSupport Team"
        )
        result = grade_response(response, email)
        assert result.total >= 0.7

    def test_empty_response(self):
        email = RESPOND_EMAILS[0]
        result = grade_response("", email)
        assert result.total == 0.0

    def test_rude_response(self):
        email = RESPOND_EMAILS[0]
        result = grade_response("That's not my problem. Deal with it.", email)
        assert result.total < 0.3
        assert any("forbidden" in p for p in result.penalties)

    def test_too_short(self):
        email = RESPOND_EMAILS[0]
        result = grade_response("OK.", email)
        assert result.breakdown["length"] < 0.5

    def test_no_greeting(self):
        email = RESPOND_EMAILS[0]
        result = grade_response(
            "We apologize for the delay. Your refund will be processed. "
            "We understand your frustration. Please let us know if you need help.",
            email,
        )
        assert result.breakdown["greeting"] == 0.0

    def test_with_greeting(self):
        email = RESPOND_EMAILS[0]
        result = grade_response(
            "Dear Customer,\nWe apologize for the delay. Your refund will be processed. "
            "We understand your frustration and will resolve this. Please be patient.",
            email,
        )
        assert result.breakdown["greeting"] == 1.0

    def test_scores_in_range(self):
        for email in RESPOND_EMAILS:
            result = grade_response("Hello, we are sorry. We will help.", email)
            assert 0.0 <= result.total <= 1.0

    def test_deterministic(self):
        email = RESPOND_EMAILS[2]
        resp = "Dear user, we apologize for the inconvenience. We will investigate."
        r1 = grade_response(resp, email)
        r2 = grade_response(resp, email)
        assert r1.total == r2.total


# ── Thread Grader ─────────────────────────────────────────────────────────────

class TestThreadGrader:
    def test_contradiction_detection(self):
        thread = THREAD_SCENARIOS[0]  # server migration
        result = grade_thread_step(
            0,
            "There is a contradiction between the CFO and sysadmin. The CFO claims "
            "the shutdown date is March 31st based on sales, but the sysadmin has "
            "confirmation from operations that the February 5th shutdown is real.",
            thread,
        )
        assert result.total >= 0.5

    def test_priority_correct(self):
        thread = THREAD_SCENARIOS[0]  # true priority is urgent
        result = grade_thread_step(1, "Priority: urgent\nJustification: critical deadline.", thread)
        assert result.total == 1.0

    def test_priority_wrong(self):
        thread = THREAD_SCENARIOS[0]
        result = grade_thread_step(1, "Priority: low\nNo rush.", thread)
        assert result.total == 0.0

    def test_resolution_with_action_items(self):
        thread = THREAD_SCENARIOS[0]
        result = grade_thread_step(
            2,
            "Action items:\n"
            "1. Verify shutdown date directly with data center operations\n"
            "2. Begin emergency migration planning\n"
            "3. Escalate to CTO for resource reallocation\n"
            "4. Request budget increase if needed",
            thread,
        )
        assert result.total >= 0.5

    def test_followup(self):
        thread = THREAD_SCENARIOS[0]
        result = grade_thread_step(
            3,
            "Schedule an emergency meeting within 24 hours with all stakeholders "
            "to review the migration timeline.",
            thread,
        )
        assert result.total >= 0.3

    def test_empty_step(self):
        thread = THREAD_SCENARIOS[0]
        result = grade_thread_step(0, "", thread)
        assert result.total == 0.0

    def test_full_thread_grading(self):
        thread = THREAD_SCENARIOS[0]
        responses = [
            "The CFO and sysadmin contradict each other about the shutdown date. "
            "CFO says March 31st, sysadmin says February 5th. This is inconsistent.",
            "Priority: urgent\nThe physical shutdown is confirmed by operations.",
            "1. Verify date with operations\n2. Begin emergency migration\n3. Escalate to CTO\n4. Budget review",
            "Schedule emergency meeting within 24 hours with all stakeholders.",
        ]
        result = grade_thread_resolution(responses, thread)
        assert 0.0 <= result.total <= 1.0
        assert len(result.breakdown) > 0

    def test_deterministic(self):
        thread = THREAD_SCENARIOS[1]
        resp = "There is a conflict about the number of records and notification timing."
        r1 = grade_thread_step(0, resp, thread)
        r2 = grade_thread_step(0, resp, thread)
        assert r1.total == r2.total

    def test_all_scores_in_range(self):
        for thread in THREAD_SCENARIOS:
            for step in range(4):
                result = grade_thread_step(step, "some response here", thread)
                assert 0.0 <= result.total <= 1.0
