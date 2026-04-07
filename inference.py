"""
Inference Script for Email Triage OpenEnv
=========================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
    LOCAL_IMAGE_NAME The name of the local image to use for the environment if you are using
                   method

- Defaults are set only for API_BASE_URL and MODEL_NAME
    (and should reflect your active inference setup):
    API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-endpoint>")
    MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")

- The inference script must be named `inference.py` and placed in the root directory of the project
- Participants must use OpenAI Client for all LLM calls using above variables

STDOUT FORMAT
- The script must emit exactly three line types to stdout, in this order:

    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>

Rules:
    - One [START] line at episode begin.
    - One [STEP] line per step, immediately after env.step() returns.
    - One [END] line after env.close(), always emitted (even on exception).
    - reward and rewards are formatted to 2 decimal places.
    - done and success are lowercase booleans: true or false.
    - error is the raw last_action_error string, or null if none.
    - All fields on a single line with no newlines within a line.
    - Each tasks should return score in [0, 1]

Example:
    [START] task=email_classify env=email_triage_env model=Qwen2.5-72B-Instruct
    [STEP] step=1 action=Priority: urgent  Category: billing reward=1.00 done=true error=null
    [END] success=true steps=1 score=1.00 rewards=1.00
"""

import os
import textwrap
from typing import Optional

from openai import OpenAI

# ── Environment imports ───────────────────────────────────────────────────────

from src.environment import EmailTriageEnv
from src.models import Action

# ── Configuration ─────────────────────────────────────────────────────────────

API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
BENCHMARK = os.getenv("EMAIL_TRIAGE_BENCHMARK", "email_triage_env")

TASK_NAMES = ["email_classify", "email_respond", "email_thread"]
MAX_STEPS_MAP = {"email_classify": 1, "email_respond": 1, "email_thread": 4}
TEMPERATURE = 0.7
MAX_TOKENS = 300
SUCCESS_SCORE_THRESHOLD = 0.1


# ── Logging helpers ───────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Ensure action has no newlines
    action_clean = action.replace("\n", " ").replace("\r", " ")
    print(
        f"[STEP] step={step} action={action_clean} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ── LLM interaction ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert email triage and customer support assistant.
    You handle email classification, response drafting, and thread resolution.

    For classification tasks: respond with exactly two lines:
    Priority: <urgent|normal|low>
    Category: <billing|technical|general|complaint|security>

    For response drafting: write a professional, empathetic reply (50-300 words).
    Start with a greeting, show empathy, propose a resolution.

    For thread resolution: follow the step instructions carefully.
    Be thorough and specific in your analysis.
""").strip()


def get_model_response(
    client: OpenAI,
    prompt: str,
    context: Optional[str] = None,
) -> str:
    """Get a response from the LLM via OpenAI-compatible API."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if context:
        messages.append({"role": "assistant", "content": f"Previous context:\n{context}"})
    messages.append({"role": "user", "content": prompt})

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else "hello"
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "hello"


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_task(client: OpenAI, env: EmailTriageEnv, task_name: str, email_idx: int) -> None:
    """Run a single task episode and emit structured logs."""
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    steps_taken = 0
    rewards: list[float] = []
    score = 0.0
    success = False

    try:
        obs = env.reset(task_id=task_name, email_index=email_idx)
        max_steps = MAX_STEPS_MAP.get(task_name, 1)

        for step_num in range(1, max_steps + 1):
            if env._done:
                break

            message = get_model_response(client, obs.prompt, obs.context)
            result = env.step(Action(message=message))

            reward = result.reward
            done = result.done
            error = None

            rewards.append(reward)
            steps_taken = step_num

            log_step(step=step_num, action=message, reward=reward, done=done, error=error)

            if done:
                break

            obs = result.observation

        score = sum(rewards) / max(len(rewards), 1)
        # Ensure score is strictly between 0 and 1 (not 0.0 or 1.0) per hackathon rules
        if score <= 0.0:
            score = 0.01
        elif score >= 1.0:
            score = 0.99
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[DEBUG] Error during task {task_name}: {e}", flush=True)
        if not rewards:
            rewards = [0.01]  # Use 0.01 instead of 0.0 per hackathon rules
            steps_taken = 1
            log_step(step=1, action="error", reward=0.01, done=True, error=str(e))
        # Ensure score is clamped even on error path
        score = sum(rewards) / max(len(rewards), 1)
        if score <= 0.0:
            score = 0.01
        elif score >= 1.0:
            score = 0.99
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = EmailTriageEnv(adaptive_difficulty=False, curriculum_mode=False)

    # Run 2 episodes per task to demonstrate reproducibility
    for task_name in TASK_NAMES:
        episodes = 2 if task_name != "email_thread" else 1  # Thread task is longer
        for ep in range(episodes):
            run_task(client, env, task_name, email_idx=ep)

    env.close()


if __name__ == "__main__":
    main()
