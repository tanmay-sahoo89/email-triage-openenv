"""Tests for the FastAPI server endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.server import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["environment"] == "email-triage-env"

    def test_health_includes_features(self, client):
        resp = client.get("/")
        data = resp.json()
        assert "features" in data
        assert "curriculum_learning" in data["features"]
        assert "streaming_grading" in data["features"]


class TestResetEndpoint:
    def test_reset_default(self, client):
        resp = client.post("/reset", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert "prompt" in data
        assert data["step"] == 0

    def test_reset_classify(self, client):
        resp = client.post("/reset", json={"task_id": "email_classify"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["task_id"] == "email_classify"
        assert data["difficulty"] == "easy"

    def test_reset_respond(self, client):
        # First unlock respond by simulating classify mastery via direct reset
        client.post("/reset", json={"task_id": "email_classify"})
        resp = client.post("/reset", json={"task_id": "email_respond"})
        # With curriculum mode, if respond not unlocked, falls back to classify
        assert resp.status_code == 200

    def test_reset_thread(self, client):
        client.post("/reset", json={"task_id": "email_classify"})
        resp = client.post("/reset", json={"task_id": "email_thread"})
        assert resp.status_code == 200

    def test_reset_invalid_task(self, client):
        resp = client.post("/reset", json={"task_id": "nonexistent"})
        assert resp.status_code == 400

    def test_reset_with_index(self, client):
        resp = client.post("/reset", json={"task_id": "email_classify", "email_index": 3})
        assert resp.status_code == 200


class TestStepEndpoint:
    def test_step_after_reset(self, client):
        client.post("/reset", json={"task_id": "email_classify"})
        resp = client.post("/step", json={"message": "Priority: urgent\nCategory: billing"})
        assert resp.status_code == 200
        data = resp.json()
        assert "reward" in data
        assert "done" in data
        assert 0.0 <= data["reward"] <= 1.0

    def test_step_returns_done(self, client):
        client.post("/reset", json={"task_id": "email_classify", "email_index": 0})
        resp = client.post("/step", json={"message": "Priority: urgent\nCategory: billing"})
        assert resp.json()["done"] is True

    def test_step_empty_message(self, client):
        client.post("/reset", json={"task_id": "email_classify"})
        resp = client.post("/step", json={"message": ""})
        assert resp.status_code == 200
        assert resp.json()["reward"] == 0.0

    def test_step_includes_curriculum_info(self, client):
        client.post("/reset", json={"task_id": "email_classify"})
        resp = client.post("/step", json={"message": "Priority: urgent\nCategory: billing"})
        data = resp.json()
        assert "info" in data
        assert "curriculum" in data["info"]
        assert "unlocked_tasks" in data["info"]["curriculum"]

    def test_multistep_thread(self, client):
        client.post("/reset", json={"task_id": "email_thread", "email_index": 0})

        r1 = client.post("/step", json={"message": "Contradiction found."})
        assert r1.json()["done"] is False

        r2 = client.post("/step", json={"message": "Priority: urgent"})
        assert r2.json()["done"] is False

        r3 = client.post("/step", json={"message": "Action items: 1. Fix 2. Test"})
        assert r3.json()["done"] is False

        r4 = client.post("/step", json={"message": "Follow up in 24 hours."})
        assert r4.json()["done"] is True


class TestStateEndpoint:
    def test_state_initial(self, client):
        resp = client.get("/state")
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert "done" in data

    def test_state_after_episode(self, client):
        client.post("/reset", json={"task_id": "email_classify", "email_index": 0})
        client.post("/step", json={"message": "Priority: urgent\nCategory: billing"})
        resp = client.get("/state")
        data = resp.json()
        assert data["done"] is True
        assert data["step"] == 1
        assert data["total_reward"] > 0

    def test_state_includes_curriculum_metadata(self, client):
        client.post("/reset", json={"task_id": "email_classify"})
        resp = client.get("/state")
        data = resp.json()
        assert "metadata" in data
        assert "curriculum_mode" in data["metadata"]
        assert "unlocked_tasks" in data["metadata"]
        assert "seen_emails" in data["metadata"]


class TestCurriculumEndpoint:
    def test_curriculum_returns_200(self, client):
        resp = client.get("/curriculum")
        assert resp.status_code == 200
        data = resp.json()
        assert "unlocked_tasks" in data
        assert "locked_tasks" in data
        assert "thresholds" in data

    def test_curriculum_classify_always_unlocked(self, client):
        resp = client.get("/curriculum")
        data = resp.json()
        assert "email_classify" in data["unlocked_tasks"]

    def test_curriculum_thresholds_present(self, client):
        resp = client.get("/curriculum")
        data = resp.json()
        assert "email_classify" in data["thresholds"]
        assert "email_respond" in data["thresholds"]
        assert "email_thread" in data["thresholds"]


class TestStreamStepEndpoint:
    def test_stream_step_returns_event_stream(self, client):
        client.post("/reset", json={"task_id": "email_classify"})
        resp = client.post(
            "/stream_step",
            json={"message": "Priority: urgent\nCategory: billing", "stream_interval": 0.01}
        )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

    def test_stream_step_emits_events(self, client):
        client.post("/reset", json={"task_id": "email_classify"})
        resp = client.post(
            "/stream_step",
            json={"message": "Priority: urgent\nCategory: billing", "stream_interval": 0.01}
        )
        content = resp.text
        assert "data:" in content
        assert "start" in content or "progress" in content or "complete" in content
