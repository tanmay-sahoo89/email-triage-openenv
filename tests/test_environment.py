"""Tests for the EmailTriageEnv environment."""

import pytest
from src.environment import EmailTriageEnv
from src.models import Action


class TestEnvironmentReset:
    def test_reset_classify(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        obs = env.reset(task_id="email_classify")
        assert obs.task_id == "email_classify"
        assert obs.difficulty == "easy"
        assert obs.step == 0
        assert obs.max_steps == 1
        assert "priority" in obs.prompt.lower() or "classify" in obs.prompt.lower()

    def test_reset_respond(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        obs = env.reset(task_id="email_respond")
        assert obs.task_id == "email_respond"
        assert obs.difficulty == "medium"

    def test_reset_thread(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        obs = env.reset(task_id="email_thread")
        assert obs.task_id == "email_thread"
        assert obs.difficulty == "hard"
        assert obs.max_steps == 4

    def test_reset_invalid_task(self):
        env = EmailTriageEnv(curriculum_mode=False)
        with pytest.raises(ValueError, match="Unknown task"):
            env.reset(task_id="nonexistent")

    def test_reset_cycles_emails(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False, avoid_repetition=False)
        obs1 = env.reset(task_id="email_classify")
        obs2 = env.reset(task_id="email_classify")
        # Different emails should be selected on consecutive resets
        assert obs1.email_data["id"] != obs2.email_data["id"]

    def test_reset_specific_index(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        obs = env.reset(task_id="email_classify", email_index=5)
        assert obs.email_data["id"] == "c06"


class TestEnvironmentStep:
    def test_step_classify_correct(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        env.reset(task_id="email_classify", email_index=0)
        result = env.step(Action(message="Priority: urgent\nCategory: billing"))
        assert result.reward == 1.0
        assert result.done is True

    def test_step_classify_partial(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        env.reset(task_id="email_classify", email_index=0)
        result = env.step(Action(message="Priority: normal\nCategory: billing"))
        assert 0.0 < result.reward < 1.0
        assert result.done is True

    def test_step_classify_wrong(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        env.reset(task_id="email_classify", email_index=0)
        result = env.step(Action(message="Priority: low\nCategory: general"))
        assert result.reward == 0.0

    def test_step_empty_response(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        env.reset(task_id="email_classify", email_index=0)
        result = env.step(Action(message=""))
        assert result.reward == 0.0

    def test_step_after_done_raises(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        env.reset(task_id="email_classify", email_index=0)
        env.step(Action(message="Priority: urgent\nCategory: billing"))
        with pytest.raises(RuntimeError, match="done"):
            env.step(Action(message="another"))

    def test_step_without_reset_raises(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        with pytest.raises(RuntimeError):
            env.step(Action(message="hello"))

    def test_multiturn_thread(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        env.reset(task_id="email_thread", email_index=0)

        # Step 1: identify contradictions
        r1 = env.step(Action(
            message="The CFO contradicts the sysadmin. CFO says March 31st, "
                    "sysadmin says February 5th. There is a discrepancy about the shutdown date."
        ))
        assert not r1.done
        assert r1.reward >= 0.0

        # Step 2: priority
        r2 = env.step(Action(message="Priority: urgent\nJustification: The physical shutdown is real."))
        assert not r2.done

        # Step 3: resolution
        r3 = env.step(Action(
            message="Action items:\n1. Verify shutdown date with operations\n"
                    "2. Begin emergency migration\n3. Escalate to CTO\n4. Request budget increase"
        ))
        assert not r3.done

        # Step 4: followup
        r4 = env.step(Action(
            message="Schedule an emergency meeting within 24 hours with all stakeholders."
        ))
        assert r4.done


class TestEnvironmentState:
    def test_state_before_reset(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        state = env.state()
        assert state.done is True
        assert state.task_id == "none"

    def test_state_after_reset(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        env.reset(task_id="email_classify")
        state = env.state()
        assert state.task_id == "email_classify"
        assert state.done is False
        assert state.step == 0

    def test_state_after_step(self):
        env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)
        env.reset(task_id="email_classify", email_index=0)
        env.step(Action(message="Priority: urgent\nCategory: billing"))
        state = env.state()
        assert state.done is True
        assert state.step == 1
        assert state.total_reward == 1.0


class TestAdaptiveDifficulty:
    def test_starts_with_easy(self):
        env = EmailTriageEnv(adaptive_difficulty=True, curriculum_mode=False)
        obs = env.reset()
        assert obs.task_id == "email_classify"

    def test_escalates_on_high_scores(self):
        env = EmailTriageEnv(adaptive_difficulty=True, curriculum_mode=False)
        # Simulate high scores
        env._recent_scores = [0.9, 0.85, 0.9, 0.88, 0.92]
        task = env._pick_adaptive_task()
        assert task == "email_thread"

    def test_stays_easy_on_low_scores(self):
        env = EmailTriageEnv(adaptive_difficulty=True, curriculum_mode=False)
        env._recent_scores = [0.2, 0.3, 0.1]
        task = env._pick_adaptive_task()
        assert task == "email_classify"


class TestCurriculumLearning:
    """Tests for the curriculum learning feature."""
    
    def test_only_classify_unlocked_initially(self):
        env = EmailTriageEnv(curriculum_mode=True, adaptive_difficulty=False)
        assert "email_classify" in env._unlocked_tasks
        assert "email_respond" not in env._unlocked_tasks
        assert "email_thread" not in env._unlocked_tasks

    def test_locked_task_falls_back(self):
        env = EmailTriageEnv(curriculum_mode=True, adaptive_difficulty=False)
        # Try to access locked task - should fall back
        obs = env.reset(task_id="email_thread")
        # Should get classify since thread is locked
        assert obs.task_id == "email_classify"

    def test_unlock_respond_after_classify_mastery(self):
        env = EmailTriageEnv(curriculum_mode=True, adaptive_difficulty=False)
        
        # Simulate getting high scores on classify
        env._task_scores["email_classify"] = [0.85, 0.90, 0.80, 0.75, 0.72]
        env._update_curriculum()
        
        # email_respond should now be unlocked
        assert "email_respond" in env._unlocked_tasks

    def test_unlock_thread_after_respond_mastery(self):
        env = EmailTriageEnv(curriculum_mode=True, adaptive_difficulty=False)
        
        # Unlock respond first
        env._unlocked_tasks.add("email_respond")
        
        # Simulate getting high scores on respond
        env._task_scores["email_respond"] = [0.70, 0.75, 0.68, 0.72, 0.65]
        env._update_curriculum()
        
        # email_thread should now be unlocked
        assert "email_thread" in env._unlocked_tasks

    def test_curriculum_in_state_metadata(self):
        env = EmailTriageEnv(curriculum_mode=True, adaptive_difficulty=False)
        env.reset(task_id="email_classify", email_index=0)
        env.step(Action(message="Priority: urgent\nCategory: billing"))
        
        state = env.state()
        assert "curriculum_mode" in state.metadata
        assert state.metadata["curriculum_mode"] is True
        assert "unlocked_tasks" in state.metadata

    def test_curriculum_in_step_info(self):
        env = EmailTriageEnv(curriculum_mode=True, adaptive_difficulty=False)
        env.reset(task_id="email_classify", email_index=0)
        result = env.step(Action(message="Priority: urgent\nCategory: billing"))
        
        assert "curriculum" in result.info
        assert "unlocked_tasks" in result.info["curriculum"]


class TestEmailSimilarityAvoidance:
    """Tests for the email similarity avoidance feature."""
    
    def test_tracks_seen_emails(self):
        env = EmailTriageEnv(avoid_repetition=True, curriculum_mode=False, adaptive_difficulty=False)
        
        obs1 = env.reset(task_id="email_classify")
        email_id_1 = obs1.email_data["id"]
        
        # Complete the episode
        env.step(Action(message="Priority: urgent\nCategory: billing"))
        
        # Check that the email was tracked
        assert email_id_1 in env._seen_emails["email_classify"]

    def test_avoids_seen_emails(self):
        env = EmailTriageEnv(avoid_repetition=True, curriculum_mode=False, adaptive_difficulty=False)
        
        seen_ids = set()
        for _ in range(5):
            obs = env.reset(task_id="email_classify")
            email_id = obs.email_data["id"]
            # Each email should be unique
            assert email_id not in seen_ids
            seen_ids.add(email_id)
            env.step(Action(message="Priority: urgent\nCategory: billing"))

    def test_resets_seen_when_all_used(self):
        env = EmailTriageEnv(avoid_repetition=True, curriculum_mode=False, adaptive_difficulty=False)
        
        # Mark all emails as seen
        from src.data.emails import CLASSIFY_EMAILS
        for email in CLASSIFY_EMAILS:
            env._seen_emails["email_classify"].add(email.id)
        
        # Should reset and start from beginning
        obs = env.reset(task_id="email_classify")
        # Should get an email (cycle restarted)
        assert obs.email_data["id"] is not None

    def test_seen_emails_in_state(self):
        env = EmailTriageEnv(avoid_repetition=True, curriculum_mode=False, adaptive_difficulty=False)
        env.reset(task_id="email_classify")
        env.step(Action(message="Priority: urgent\nCategory: billing"))
        
        state = env.state()
        assert "seen_emails" in state.metadata
        assert state.metadata["seen_emails"]["email_classify"] == 1
