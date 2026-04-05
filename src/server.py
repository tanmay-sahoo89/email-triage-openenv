"""FastAPI server implementing OpenEnv HTTP interface."""

from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
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


# ── Application ───────────────────────────────────────────────────────────────

env: EmailTriageEnv | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global env
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


@app.get("/", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        environment="email-triage-env",
        version="1.0.0",
        features=[
            "curriculum_learning",
            "adaptive_difficulty", 
            "email_similarity_avoidance",
            "streaming_grading",
            "multi_turn_episodes",
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
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    action = Action(message=request.message)

    try:
        result = env.step(action)
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


def start_server(host: str = "0.0.0.0", port: int = 7860):
    """Start the server (used by Dockerfile CMD)."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
