"""Tests for the inference script — validates structured output format."""

import re
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

# Import inference components
from inference import (
    log_start,
    log_step,
    log_end,
    TASK_NAMES,
    SUCCESS_SCORE_THRESHOLD,
)


class TestLoggingFormat:
    """Tests for the structured logging format compliance."""

    def test_log_start_format(self, capsys):
        log_start(task="email_classify", env="test_env", model="test-model")
        captured = capsys.readouterr()
        assert captured.out.strip() == "[START] task=email_classify env=test_env model=test-model"

    def test_log_step_format(self, capsys):
        log_step(step=1, action="Priority: urgent", reward=0.85, done=False, error=None)
        captured = capsys.readouterr()
        line = captured.out.strip()
        assert line.startswith("[STEP]")
        assert "step=1" in line
        assert "action=Priority: urgent" in line
        assert "reward=0.85" in line
        assert "done=false" in line
        assert "error=null" in line

    def test_log_step_with_error(self, capsys):
        log_step(step=2, action="test", reward=0.0, done=True, error="Something went wrong")
        captured = capsys.readouterr()
        line = captured.out.strip()
        assert "error=Something went wrong" in line

    def test_log_step_removes_newlines(self, capsys):
        log_step(step=1, action="Line1\nLine2\rLine3", reward=0.5, done=False, error=None)
        captured = capsys.readouterr()
        line = captured.out.strip()
        assert "\n" not in line.split("action=")[1].split(" reward=")[0]
        assert "\r" not in line

    def test_log_end_format(self, capsys):
        log_end(success=True, steps=3, score=0.75, rewards=[0.8, 0.7, 0.75])
        captured = capsys.readouterr()
        line = captured.out.strip()
        assert line.startswith("[END]")
        assert "success=true" in line
        assert "steps=3" in line
        assert "score=0.75" in line
        assert "rewards=0.80,0.70,0.75" in line

    def test_log_end_failure(self, capsys):
        log_end(success=False, steps=1, score=0.0, rewards=[0.0])
        captured = capsys.readouterr()
        line = captured.out.strip()
        assert "success=false" in line

    def test_reward_format_two_decimals(self, capsys):
        log_step(step=1, action="test", reward=0.333333, done=True, error=None)
        captured = capsys.readouterr()
        # Should be formatted to 2 decimal places
        assert "reward=0.33" in captured.out

    def test_done_lowercase_boolean(self, capsys):
        log_step(step=1, action="test", reward=0.5, done=True, error=None)
        captured = capsys.readouterr()
        assert "done=true" in captured.out
        assert "done=True" not in captured.out


class TestInferenceConfiguration:
    """Tests for inference script configuration."""

    def test_task_names_defined(self):
        assert "email_classify" in TASK_NAMES
        assert "email_respond" in TASK_NAMES
        assert "email_thread" in TASK_NAMES
        assert len(TASK_NAMES) == 3

    def test_success_threshold_in_range(self):
        assert 0.0 <= SUCCESS_SCORE_THRESHOLD <= 1.0


class TestEndToEndInference:
    """Integration tests for the inference workflow."""

    def test_run_task_with_mock_client(self):
        """Test that run_task produces valid output format."""
        from src.environment import EmailTriageEnv
        from inference import run_task

        # Create a mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Priority: urgent\nCategory: billing"
        mock_client.chat.completions.create.return_value = mock_response

        # Capture stdout
        env = EmailTriageEnv(adaptive_difficulty=False)

        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            run_task(mock_client, env, "email_classify", email_idx=0)

        output = captured_output.getvalue()
        lines = output.strip().split("\n")

        # Verify output format
        assert any(line.startswith("[START]") for line in lines)
        assert any(line.startswith("[STEP]") for line in lines)
        assert any(line.startswith("[END]") for line in lines)

        # Verify START line format
        start_line = [l for l in lines if l.startswith("[START]")][0]
        assert "task=email_classify" in start_line
        assert "model=" in start_line

        # Verify END line format
        end_line = [l for l in lines if l.startswith("[END]")][0]
        assert "success=" in end_line
        assert "steps=" in end_line
        assert "score=" in end_line
        assert "rewards=" in end_line

        env.close()


class TestOutputLineValidation:
    """Regex-based validation of output line format."""

    START_PATTERN = r"^\[START\] task=\S+ env=\S+ model=\S+$"
    STEP_PATTERN = r"^\[STEP\] step=\d+ action=.+ reward=\d+\.\d{2} done=(true|false) error=.+$"
    END_PATTERN = r"^\[END\] success=(true|false) steps=\d+ score=\d+\.\d{2} rewards=[\d\.,]+$"

    def test_start_line_regex(self):
        line = "[START] task=email_classify env=email_triage_env model=Qwen/Qwen2.5-72B-Instruct"
        assert re.match(self.START_PATTERN, line)

    def test_step_line_regex(self):
        line = "[STEP] step=1 action=Priority: urgent  Category: billing reward=1.00 done=true error=null"
        assert re.match(self.STEP_PATTERN, line)

    def test_end_line_regex(self):
        line = "[END] success=true steps=1 score=1.00 rewards=1.00"
        assert re.match(self.END_PATTERN, line)

    def test_end_line_multiple_rewards(self):
        line = "[END] success=true steps=4 score=0.75 rewards=0.80,0.70,0.65,0.85"
        assert re.match(self.END_PATTERN, line)
