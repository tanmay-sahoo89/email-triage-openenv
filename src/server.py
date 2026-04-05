"""FastAPI server implementing OpenEnv HTTP interface."""

from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from src.environment import EmailTriageEnv
from src.models import Action


# ── Request / Response schemas ────────────────────────────────────────────────

class ResetRequest(BaseModel):
    task_id: str | None = None
    email_index: int | None = None


class StepRequest(BaseModel):
    message: str


class StreamStepRequest(BaseModel):
    """Request for streaming step - allows partial responses."""
    message: str
    stream_interval: float = 0.1  # Seconds between grading updates


class ObservationResponse(BaseModel):
    task_id: str
    task_name: str
    difficulty: str
    prompt: str
    email_data: dict[str, Any]
    step: int
    max_steps: int
    context: str | None = None


class StepResponse(BaseModel):
    observation: ObservationResponse
    reward: float
    done: bool
    info: dict[str, Any]


class StateResponse(BaseModel):
    task_id: str
    task_name: str
    difficulty: str
    step: int
    max_steps: int
    done: bool
    total_reward: float
    rewards: list[float]
    metadata: dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    features: list[str]


class CurriculumResponse(BaseModel):
    """Response showing curriculum learning status."""
    unlocked_tasks: list[str]
    locked_tasks: list[str]
    task_averages: dict[str, float]
    thresholds: dict[str, float]


class MetricsResponse(BaseModel):
    """Aggregate metrics for the environment."""
    total_episodes: int
    total_steps: int
    per_task_stats: dict[str, dict[str, Any]]
    best_scores: dict[str, float]
    recent_scores: list[float]
    uptime_seconds: float


class ReplayResponse(BaseModel):
    """Episode replay data."""
    task_id: str
    steps: list[dict[str, Any]]
    total_reward: float
    success: bool


class ConfigureRequest(BaseModel):
    """Configure environment parameters."""
    difficulty_mode: str | None = None  # easy, normal, hard
    adaptive_difficulty: bool | None = None
    curriculum_mode: bool | None = None
    grader_weights: dict[str, float] | None = None


# ── Application ───────────────────────────────────────────────────────────────

env: EmailTriageEnv | None = None
episode_history: list[dict] = []  # Store episode replays
start_time: float = 0.0
total_steps: int = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global env, start_time
    import time
    start_time = time.time()
    env = EmailTriageEnv(
        adaptive_difficulty=True,
        curriculum_mode=True,
        avoid_repetition=True,
    )
    yield
    if env is not None:
        env.close()


app = FastAPI(
    title="Email Triage OpenEnv",
    description="A real-world OpenEnv environment for email triage and response.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = Path(__file__).parent.parent / "public" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/x-icon")
    return Response(status_code=204)


@app.get("/", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        environment="email-triage-env",
        version="1.1.0",
        features=[
            "curriculum_learning",
            "adaptive_difficulty", 
            "email_similarity_avoidance",
            "streaming_grading",
            "multi_turn_episodes",
            "hindsight_feedback",
            "per_criterion_explanations",
            "hint_system",
            "metrics_analytics",
            "episode_replay",
            "dynamic_configuration",
            "leaderboard",
        ],
    )


@app.post("/reset", response_model=ObservationResponse)
async def reset(request: ResetRequest | None = None):
    """Reset environment and start a new episode."""
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    task_id = request.task_id if request else None
    email_index = request.email_index if request else None

    try:
        obs = env.reset(task_id=task_id, email_index=email_index)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ObservationResponse(**obs.model_dump())


@app.post("/step", response_model=StepResponse)
async def step(request: StepRequest):
    """Execute one step with the given action."""
    global total_steps
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    action = Action(message=request.message)

    try:
        result = env.step(action)
        total_steps += 1
        
        # Track episode for replay
        if result.done and episode_history is not None:
            episode_history.append({
                "task_id": env._task_id,
                "total_reward": result.info.get("total_reward", 0),
                "steps": env._step,
                "timestamp": __import__("time").time(),
            })
            # Keep only last 100 episodes
            if len(episode_history) > 100:
                episode_history.pop(0)
                
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StepResponse(
        observation=ObservationResponse(**result.observation.model_dump()),
        reward=result.reward,
        done=result.done,
        info=result.info,
    )


async def _stream_grading(message: str, interval: float) -> AsyncGenerator[str, None]:
    """Stream grading feedback as Server-Sent Events."""
    if env is None:
        yield f"data: {json.dumps({'error': 'Environment not initialized'})}\n\n"
        return
    
    # Emit start event
    yield f"data: {json.dumps({'event': 'start', 'message_length': len(message)})}\n\n"
    await asyncio.sleep(interval)
    
    # Simulate progressive grading feedback (in real use, this could grade chunks)
    task_id = env._task_id
    
    if task_id == "email_classify":
        criteria = ["parsing_response", "checking_priority", "checking_category", "applying_bonuses"]
    elif task_id == "email_respond":
        criteria = ["checking_tone", "checking_relevance", "checking_length", 
                    "checking_forbidden", "checking_greeting", "checking_empathy"]
    elif task_id == "email_thread":
        step_names = ["analyzing_contradictions", "evaluating_priority", 
                       "scoring_resolution", "checking_followup"]
        criteria = [step_names[min(env._step, len(step_names) - 1)]]
    else:
        criteria = ["grading"]
    
    for i, criterion in enumerate(criteria):
        progress = (i + 1) / len(criteria)
        yield f"data: {json.dumps({'event': 'progress', 'criterion': criterion, 'progress': round(progress, 2)})}\n\n"
        await asyncio.sleep(interval)
    
    # Execute actual step
    try:
        action = Action(message=message)
        result = env.step(action)
        
        # Emit final result
        final_data = {
            "event": "complete",
            "reward": result.reward,
            "done": result.done,
            "info": result.info,
            "observation": result.observation.model_dump(),
        }
        yield f"data: {json.dumps(final_data)}\n\n"
        
    except RuntimeError as e:
        yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"


@app.post("/stream_step")
async def stream_step(request: StreamStepRequest):
    """Execute a step with streaming grading feedback.
    
    Returns Server-Sent Events with progress updates:
    - start: Beginning grading
    - progress: Per-criterion grading progress
    - complete: Final result with reward and observation
    - error: If something went wrong
    """
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    
    return StreamingResponse(
        _stream_grading(request.message, request.stream_interval),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/curriculum", response_model=CurriculumResponse)
async def curriculum():
    """Get curriculum learning status - shows which tasks are unlocked."""
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    
    all_tasks = {"email_classify", "email_respond", "email_thread"}
    unlocked = env._unlocked_tasks
    locked = all_tasks - unlocked
    
    task_averages = {}
    for task, scores in env._task_scores.items():
        if scores:
            task_averages[task] = round(sum(scores[-5:]) / len(scores[-5:]), 2)
    
    return CurriculumResponse(
        unlocked_tasks=sorted(list(unlocked)),
        locked_tasks=sorted(list(locked)),
        task_averages=task_averages,
        thresholds=env.CURRICULUM_THRESHOLDS,
    )


@app.get("/state", response_model=StateResponse)
async def state():
    """Get current environment state."""
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    s = env.state()
    return StateResponse(**s.model_dump())


@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    """Get aggregate metrics and statistics for the environment.
    
    Innovative feature: Provides analytics on agent performance across tasks.
    """
    import time
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    
    per_task_stats = {}
    best_scores: dict[str, float] = {}
    
    for task_id, scores in env._task_scores.items():
        if scores:
            per_task_stats[task_id] = {
                "episodes": len(scores),
                "avg_score": round(sum(scores) / len(scores), 3),
                "min_score": round(min(scores), 3),
                "max_score": round(max(scores), 3),
                "recent_avg": round(sum(scores[-5:]) / len(scores[-5:]), 3),
            }
            best_scores[task_id] = round(max(scores), 3)
        else:
            per_task_stats[task_id] = {
                "episodes": 0, "avg_score": 0, "min_score": 0, "max_score": 0, "recent_avg": 0
            }
            best_scores[task_id] = 0.0
    
    return MetricsResponse(
        total_episodes=env._episode_count,
        total_steps=total_steps,
        per_task_stats=per_task_stats,
        best_scores=best_scores,
        recent_scores=[round(s, 2) for s in env._recent_scores[-10:]],
        uptime_seconds=round(time.time() - start_time, 2),
    )


@app.get("/replay")
async def replay(limit: int = 10):
    """Get recent episode history for replay/analysis.
    
    Innovative feature: Allows agents to review past episodes for learning.
    """
    return {
        "episodes": episode_history[-limit:],
        "total_episodes": len(episode_history),
    }


@app.post("/configure")
async def configure(request: ConfigureRequest):
    """Configure environment parameters dynamically.
    
    Innovative feature: Researchers can adjust settings without restart.
    """
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    
    changes = []
    
    if request.adaptive_difficulty is not None:
        env._adaptive = request.adaptive_difficulty
        changes.append(f"adaptive_difficulty={request.adaptive_difficulty}")
    
    if request.curriculum_mode is not None:
        env._curriculum_mode = request.curriculum_mode
        changes.append(f"curriculum_mode={request.curriculum_mode}")
        # If turning off curriculum mode, unlock all tasks
        if not request.curriculum_mode:
            env._unlocked_tasks = {"email_classify", "email_respond", "email_thread"}
    
    return {
        "status": "configured",
        "changes": changes,
        "current_config": {
            "adaptive_difficulty": env._adaptive,
            "curriculum_mode": env._curriculum_mode,
            "avoid_repetition": env._avoid_repetition,
        }
    }


@app.get("/leaderboard")
async def leaderboard():
    """Get leaderboard showing best scores per task.
    
    Innovative feature: Tracks and displays best performance.
    """
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    
    leaderboard_data = []
    for task_id in ["email_classify", "email_respond", "email_thread"]:
        scores = env._task_scores.get(task_id, [])
        if scores:
            leaderboard_data.append({
                "task": task_id,
                "best_score": round(max(scores), 3),
                "attempts": len(scores),
                "avg_score": round(sum(scores) / len(scores), 3),
                "perfect_runs": sum(1 for s in scores if s >= 0.95),
            })
        else:
            leaderboard_data.append({
                "task": task_id,
                "best_score": 0.0,
                "attempts": 0,
                "avg_score": 0.0,
                "perfect_runs": 0,
            })
    
    return {
        "leaderboard": leaderboard_data,
        "total_episodes": env._episode_count,
    }


@app.get("/hints/{task_id}")
async def get_hints(task_id: str):
    """Get task-specific hints for struggling agents.
    
    Innovative feature: Provides guidance without giving away answers.
    """
    hints = {
        "email_classify": [
            "Look for urgency keywords: 'URGENT', 'immediately', 'asap', 'critical'",
            "Priority: urgent (needs action now), normal (routine), low (informational)",
            "Categories: billing (payments/invoices), technical (bugs/errors), security (threats/phishing)",
            "Watch for phishing indicators: suspicious links, urgency + personal info requests",
        ],
        "email_respond": [
            "Always start with a professional greeting (Dear, Hello, Hi)",
            "Show empathy: 'I understand', 'I apologize', 'I'm sorry to hear'",
            "Be solution-focused: 'We will', 'I'll ensure', 'Let me help'",
            "Keep responses 50-300 words for optimal scores",
            "Avoid dismissive phrases: 'not my problem', 'deal with it'",
            "End with a follow-up commitment: 'I'll keep you updated'",
        ],
        "email_thread": [
            "Step 1: Identify specific contradictions between emails",
            "Step 2: Determine priority based on impact and urgency",
            "Step 3: Draft resolution with numbered action items",
            "Step 4: Recommend follow-up with specific people and timeline",
            "Look for who said what - senders often have conflicting information",
        ],
    }
    
    if task_id not in hints:
        raise HTTPException(status_code=404, detail=f"Unknown task: {task_id}")
    
    return {
        "task_id": task_id,
        "hints": hints[task_id],
        "difficulty": {"email_classify": "easy", "email_respond": "medium", "email_thread": "hard"}[task_id],
    }


def start_server(host: str = "0.0.0.0", port: int = 7860):
    """Start the server (used by Dockerfile CMD)."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
