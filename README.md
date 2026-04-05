---
title: Email Triage Env
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# 📧 Email Triage & Response — OpenEnv Environment

[![OpenEnv](https://img.shields.io/badge/OpenEnv-1.1.0-blue)](https://github.com/huggingface/openenv)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face%20Spaces-orange)](https://huggingface.co/spaces)
[![Version](https://img.shields.io/badge/Version-1.1.0-blueviolet)]()
[![Features](https://img.shields.io/badge/Features-17-success)]()

> **Meta x Hugging Face OpenEnv Hackathon Submission**

A production-ready OpenEnv environment where AI agents learn to triage, classify, and respond to emails. This simulates a real customer support workflow that companies use daily — not a game or toy environment.

---

## 🏆 Why This Project Wins

### 1. **Real-World Problem** 💼
- **Not a toy task**: Email triage is an actual customer support workflow
- **Business value**: Companies spend millions on email management systems
- **Practical impact**: Agents learn skills applicable to real support teams

### 2. **17 Innovative Features** ⭐
Most competing environments have 5-7 features. We have **17**:
- ✅ Curriculum learning (progressive task unlocking)
- ✅ Hindsight feedback (ideal responses shown for learning)
- ✅ Per-criterion explanations (why each score)
- ✅ Metrics & leaderboard (track progress)
- ✅ Dynamic configuration (tune without redeploying)
- ✅ Episode replay (learn from history)
- ✅ Streaming grading (real-time feedback)
- ✅ Multi-turn reasoning (4-step problem solving)
- ✅ Edge case handling (robustness)
- ✅ + 8 more innovation features

### 3. **Production Quality** 🚀
- **Type hints**: Full type annotations for IDE support
- **Deterministic graders**: Reproducible scoring
- **Comprehensive tests**: 4 test suites, 17+ validation checks
- **Docker containerized**: Deploy anywhere
- **API-first design**: Works with any LLM provider

### 4. **Agent Learning Optimization** 🧠
- **Curriculum learning**: Tasks unlock progressively (easy→medium→hard)
- **Hindsight feedback**: Shows ideal responses for faster learning
- **Adaptive difficulty**: Auto-escalates when agent excels
- **Email similarity avoidance**: Prevents memorization, ensures generalization
- **Rich reward signals**: 6-10 criteria per task

### 5. **Research-Friendly** 📊
- **Metrics dashboard**: Aggregate stats via `/metrics`
- **Leaderboard**: Compare scores across agents
- **Episode history**: Replay and analyze episodes
- **Configurable**: Adjust settings via API without code changes
- **Hint system**: Struggling agents get hints

### 6. **Technical Excellence** 💻
- **FastAPI**: Modern, fast Python web framework
- **Pydantic validation**: Strong type safety
- **Streaming responses**: Real-time feedback via SSE
- **11 API endpoints**: Comprehensive interface
- **No hardcoded paths**: Fully portable across systems

---

## 📚 Quick Feature Overview

### Core Tasks (3 difficulty levels)

| Task | Difficulty | Purpose | Reward Criteria |
|------|-----------|---------|-----------------|
| **Email Classification** | Easy | Classify priority & category | Priority (50%) + Category (50%) |
| **Response Drafting** | Medium | Write professional reply | Tone + Relevance + Length + Grammar + Greeting + Empathy |
| **Thread Resolution** | Hard | Analyze contradictions | Contradictions + Priority + Resolution + Follow-up |

### Curriculum Learning Flow

```
Agent starts → ALWAYS UNLOCK email_classify (easy)
                        ↓
            Agent scores 70%+ on classify?
                        ↓
                YES → UNLOCK email_respond (medium)
                        ↓
            Agent scores 65%+ on respond?
                        ↓
                YES → UNLOCK email_thread (hard)
```

### New v1.1.0 Features Explained

#### 💡 **Hindsight Feedback**
After grading, the agent sees what a perfect response looks like:
```json
{
  "ideal_response": "Priority: urgent\nCategory: billing",
  "explanations": {
    "priority": "Correct! 'urgent' matches exactly.",
    "category": "Partial: 'general' is close but should be 'billing'"
  }
}
```
*Why it helps: Agents learn by example, speeds up convergence*

#### 📊 **Metrics & Analytics** (`/metrics` endpoint)
Track aggregate performance:
```json
{
  "total_episodes": 1234,
  "per_task_stats": {
    "email_classify": {
      "episodes": 450,
      "avg_score": 0.85,
      "best_score": 1.0
    }
  },
  "uptime_seconds": 86400
}
```
*Why it matters: Researchers monitor agent learning progress*

#### 🏆 **Leaderboard** (`/leaderboard` endpoint)
Compare performance across agents:
```json
{
  "leaderboard": [
    {
      "task": "email_classify",
      "best_score": 0.98,
      "perfect_runs": 25,
      "avg_score": 0.82
    }
  ]
}
```
*Why it's useful: Motivate agents, benchmark improvements*

#### 💬 **Hint System** (`/hints/{task_id}` endpoint)
Help struggling agents without spoiling answers:
- Struggling on classification? → Hint: "Look for urgency keywords"
- Stuck on response? → Hint: "Always start with a greeting"
- Hard on thread? → Hint: "Identify who said what first"

#### ⚙️ **Dynamic Configuration** (`/configure` endpoint)
Adjust settings without redeploying:
```bash
curl -X POST /configure -d '{
  "curriculum_mode": false,
  "adaptive_difficulty": true
}'
```
*Why it's powerful: Researchers experiment without downtime*

#### 🔁 **Episode Replay** (`/replay` endpoint)
Review past episodes for debugging and analysis:
```bash
curl /replay?limit=10  # Get last 10 episodes
```

---

## 🎯 How This Compares to Other Submissions

| Feature | Typical Project | Email Triage Env |
|---------|-----------------|-----------------|
| **Number of Tasks** | 1-2 | 3 with curriculum |
| **Endpoints** | 3-5 | **11 endpoints** |
| **Features** | 5-7 | **17 features** |
| **Learning Feedback** | Binary reward | Per-criterion + hindsight |
| **Agent Assistance** | None | Hints + metrics + examples |
| **Dynamic Config** | No | Yes (/configure) |
| **Analytics** | Basic | Advanced (/metrics, /leaderboard) |
| **Real-world Task** | Synthetic | **Email triage** (actual customer support) |
| **Code Quality** | Good | **Production-grade** (typed, tested, documented) |

---

## 🏗️ Architecture

<p align="center">
  <img src="public/email_triage_env.png" alt="Email Triage Environment Architecture" width="800"/>
</p>

### Architecture Flow Explained

The system follows an **Agent-Environment interaction loop** typical of reinforcement learning:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AGENT (LLM)                                    │
│                    Qwen2.5-72B / GPT-4 / Claude etc.                        │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ Action (text response)
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI SERVER                                      │
│  ┌─────────┐  ┌─────────┐  ┌──────────────┐  ┌────────────┐                │
│  │ /reset  │  │ /step   │  │ /stream_step │  │ /curriculum│                │
│  └────┬────┘  └────┬────┘  └──────┬───────┘  └─────┬──────┘                │
│       │            │              │                │                        │
│       ▼            ▼              ▼                ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      ENVIRONMENT CORE                               │   │
│  │  • State Management (current task, step, context)                   │   │
│  │  • Email Similarity Avoidance (prevents memorization)               │   │
│  │  • Adaptive Difficulty (auto-escalates when score > 0.8)            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  TASK: CLASSIFY │  │  TASK: RESPOND  │  │  TASK: THREAD   │
│    (Easy)       │  │    (Medium)     │  │    (Hard)       │
│  • 1 step       │  │  • 1 step       │  │  • 4 steps      │
│  • 12 emails    │  │  • 10 emails    │  │  • 5 threads    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ CLASSIFY GRADER │  │ RESPOND GRADER  │  │ THREAD GRADER   │
│ • Priority 50%  │  │ • Tone 25%      │  │ • Contradict 30%│
│ • Category 50%  │  │ • Relevance 25% │  │ • Priority 20%  │
│ • Bonus: phish  │  │ • Length 15%    │  │ • Resolution 25%│
│   /escalation   │  │ • Forbidden 15% │  │ • Follow-up 15% │
│                 │  │ • Greeting 10%  │  │ • Coherence 10% │
│                 │  │ • Empathy 10%   │  │                 │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REWARD SIGNAL                                       │
│  • Score: 0.0 - 1.0 (with bonus up to 1.15)                                │
│  • Detailed feedback per criterion                                          │
│  • Edge case penalties (empty, adversarial, too long)                       │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ Observation + Reward
                               ▼
                         Back to AGENT
```

**Key Flow Steps:**

1. **Reset** → Agent requests a task via `/reset` with optional `task_id` and `email_index`
2. **Observe** → Environment returns email content with task-specific instructions
3. **Act** → Agent submits text response via `/step` or `/stream_step`
4. **Grade** → Task-specific grader computes deterministic reward (0.0–1.0)
5. **Learn** → Agent receives observation + reward, loop continues

**Curriculum Progression:**

- Tasks unlock based on performance: `classify` (always) → `respond` (≥70%) → `thread` (≥65%)
- Curriculum status available via `/curriculum` endpoint

## Environment Description

Agents interact with a stream of realistic emails and must:

1. **Classify** emails by priority and category (easy)
2. **Draft professional responses** to customer complaints (medium)
3. **Resolve multi-email threads** with contradicting information (hard)

The environment provides meaningful partial-credit rewards, deterministic grading, and adaptive difficulty scaling.

## Action & Observation Spaces

### Observation Space (text)

Each observation contains:

- **task_id**: which task is active
- **prompt**: the email content with task instructions
- **email_data**: structured email metadata (sender, subject, timestamp, etc.)
- **step / max_steps**: current progress in the episode
- **context**: previous responses (for multi-turn tasks)

### Action Space (text)

Free-form text response from the agent. The format depends on the task:

- **Classification**: two lines — `Priority: <level>` and `Category: <type>`
- **Response drafting**: professional email reply (50–300 words)
- **Thread resolution**: step-by-step analysis across 4 turns

## Tasks

| Task             | Difficulty | Steps | Description                                                                                             |
| ---------------- | ---------- | ----- | ------------------------------------------------------------------------------------------------------- |
| `email_classify` | Easy       | 1     | Classify email priority (urgent/normal/low) and category (billing/technical/general/complaint/security) |
| `email_respond`  | Medium     | 1     | Draft empathetic, professional response to a customer complaint                                         |
| `email_thread`   | Hard       | 4     | Multi-turn: identify contradictions → determine priority → draft resolution → recommend follow-up       |

### Task Descriptions & Expected Difficulty

**Email Classification (Easy)**: Agent receives a single email and must identify its priority level and category. Perfect score requires exact match on both fields. Partial credit for off-by-one priority. 12 diverse emails including phishing attempts and emotional escalations.

**Response Drafting (Medium)**: Agent receives a customer complaint and must craft a professional reply. Graded on 6 criteria: tone (25%), relevance (25%), length (15%), forbidden phrases (15%), greeting (10%), empathy (10%). 10 complaint emails covering billing, technical, legal, and interpersonal issues.

**Thread Resolution (Hard)**: Agent receives a multi-email thread with contradicting claims from different senders. Must complete 4 steps: identify contradictions, determine true priority, draft resolution with action items, and recommend follow-up. 5 complex thread scenarios covering technical, security, budget, product, and HR domains.

## Reward Function

All scores are in `[0.0, 1.0]`. Graders are fully deterministic and reproducible.

### Classification Grader

- Priority match: exact = 0.5, off-by-one = 0.25, wrong = 0.0
- Category match: exact = 0.5, wrong = 0.0
- Bonus: +0.10 for detecting phishing, +0.05 for noting emotional escalation

### Response Grader

| Criterion    | Weight | What it measures                             |
| ------------ | ------ | -------------------------------------------- |
| Tone         | 0.25   | Professional language markers, no rude words |
| Relevance    | 0.25   | Keyword overlap with original email          |
| Length       | 0.15   | 50–300 words ideal range                     |
| No-forbidden | 0.15   | Avoids dismissive/rude phrases               |
| Greeting     | 0.10   | Starts with professional greeting            |
| Empathy      | 0.10   | Contains apology/empathy markers             |

Bonuses: +0.05 for proactive follow-up, +0.05 for de-escalation skills.

### Thread Grader (per-step weights)

| Step              | Weight | What it measures                                   |
| ----------------- | ------ | -------------------------------------------------- |
| 1. Contradictions | 0.30   | Identifies specific contradictions between senders |
| 2. Priority       | 0.20   | Correct priority determination with justification  |
| 3. Resolution     | 0.25   | Actionable plan with structured items              |
| 4. Follow-up      | 0.15   | Specific timing and participant recommendations    |

### Edge Case Handling

- Empty responses → 0.0 reward
- Adversarial/nonsense → penalized (alpha ratio check)
- Excessively long responses → -0.15 penalty
- Single-word responses → 80% reduction

## Baseline Scores

Tested with `Qwen/Qwen2.5-72B-Instruct` via Hugging Face Inference API:

| Task           | Avg Score | Notes                                             |
| -------------- | --------- | ------------------------------------------------- |
| email_classify | ~0.85     | Usually gets both fields correct                  |
| email_respond  | ~0.70     | Good tone/empathy, sometimes misses length target |
| email_thread   | ~0.50     | Contradictions hard to fully enumerate            |

## Setup & Usage

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn src.server:app --host 0.0.0.0 --port 7860

# Run tests
pytest tests/ -v

# Run inference
API_BASE_URL=https://router.huggingface.co/v1 \
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct \
HF_TOKEN=your_token \
python inference.py
```

### Docker

```bash
# Build
docker build -t email-triage-env .

# Run
docker run -p 7860:7860 \
  -e API_BASE_URL=https://router.huggingface.co/v1 \
  -e MODEL_NAME=Qwen/Qwen2.5-72B-Instruct \
  -e HF_TOKEN=your_token \
  email-triage-env
```

### API Endpoints

| Method | Path           | Description                                                                |
| ------ | -------------- | -------------------------------------------------------------------------- |
| GET    | `/`            | Health check with feature list                                             |
| POST   | `/reset`       | Start new episode. Body: `{"task_id": "email_classify", "email_index": 0}` |
| POST   | `/step`        | Agent action. Body: `{"message": "Priority: urgent\nCategory: billing"}`   |
| POST   | `/stream_step` | Streaming step with SSE grading feedback                                   |
| GET    | `/state`       | Current environment state                                                  |
| GET    | `/curriculum`  | Curriculum learning status and unlocked tasks                              |
| GET    | `/metrics`     | Aggregate statistics and analytics                                         |
| GET    | `/leaderboard` | Best scores per task and performance tracking                              |
| GET    | `/replay`      | Episode history for replay and analysis                                    |
| GET    | `/hints/{task_id}` | Task-specific hints for struggling agents                              |
| POST   | `/configure`   | Dynamically configure environment parameters                               |

### Deploy to Hugging Face Spaces

```bash
# Push to HF Space
openenv push --repo-id your-username/email-triage-env
```

## Innovative Features

### 🎓 Curriculum Learning Mode

Tasks unlock progressively based on agent performance:

- **email_classify** (easy): Always available
- **email_respond** (medium): Unlocks when classify avg ≥ 70%
- **email_thread** (hard): Unlocks when respond avg ≥ 65%

```bash
# Check curriculum status
curl http://localhost:7860/curriculum
```

### 📡 Streaming Grading Feedback

Real-time grading progress via Server-Sent Events:

```bash
curl -X POST http://localhost:7860/stream_step \
  -H "Content-Type: application/json" \
  -d '{"message": "Priority: urgent\nCategory: billing"}'
```

Events emitted: `start` → `progress` (per-criterion) → `complete`

### 🔄 Email Similarity Avoidance

Tracks seen emails per session to prevent memorization:

- Each task maintains a seen-email set
- New episodes prioritize unseen emails
- Auto-resets when all emails exhausted

### Other Features

- **Adaptive difficulty**: Automatically escalates to harder tasks when agent scores >0.8
- **Multi-turn episodes**: Hard task requires 4-step reasoning chain
- **Rich grader feedback**: Per-criterion breakdowns with actionable improvement hints
- **Phishing detection bonus**: Extra reward for identifying phishing/scam emails
- **De-escalation bonus**: Extra reward for appropriate emotional de-escalation
- **Proactive follow-up bonus**: Extra reward for suggesting next steps
- **Edge case robustness**: Handles empty, adversarial, and excessively long responses

### 🆕 New in v1.1.0

#### 💡 Hindsight Feedback
After grading, the environment returns the **ideal response** so agents can learn from examples:

```json
{
  "reward_detail": {
    "ideal_response": "Priority: urgent\nCategory: billing",
    "explanations": {
      "priority": "Correct! 'urgent' matches exactly.",
      "category": "Incorrect: expected 'billing', got 'technical'."
    }
  }
}
```

#### 📊 Metrics & Analytics
Track aggregate performance via `/metrics`:

```bash
curl http://localhost:7860/metrics
```

Returns: total episodes, per-task stats (avg/min/max scores), uptime, etc.

#### 🏆 Leaderboard
Track best scores and perfect runs via `/leaderboard`:

```bash
curl http://localhost:7860/leaderboard
```

#### 💬 Hint System
Get task-specific hints for struggling agents:

```bash
curl http://localhost:7860/hints/email_classify
```

#### ⚙️ Dynamic Configuration
Adjust environment parameters without restart:

```bash
curl -X POST http://localhost:7860/configure \
  -H "Content-Type: application/json" \
  -d '{"curriculum_mode": false, "adaptive_difficulty": true}'
```

#### 🔁 Episode Replay
Review past episodes for analysis:

```bash
curl http://localhost:7860/replay?limit=10
```

## 📁 Project Structure

```
my_env/
├── openenv.yaml              # OpenEnv specification (env name, version, tasks, endpoints)
├── Dockerfile                # Container definition (python:3.11-slim, port 7860)
├── inference.py              # Baseline inference script with OpenAI Client
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Python packaging configuration
├── validate.py               # Pre-submission validation script
├── README.md                 # This documentation
│
├── public/                   # Static assets
│   ├── email_triage_env.png  # Architecture diagram (PNG)
│   └── email_triage_env.svg  # Architecture diagram (SVG)
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── models.py             # Pydantic models (Observation, Action, Reward, State)
│   ├── environment.py        # Main OpenEnv class (step/reset/state)
│   ├── reward.py             # Reward computation with edge case handling
│   ├── server.py             # FastAPI server exposing API endpoints
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── emails.py         # 27+ synthetic emails across all tasks
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract base task class
│   │   ├── email_classify.py # Easy: classify by priority + category
│   │   ├── email_respond.py  # Medium: draft professional reply
│   │   └── email_thread.py   # Hard: multi-turn thread resolution
│   │
│   └── graders/
│       ├── __init__.py
│       ├── classify_grader.py # Priority + category matching (0.0–1.0)
│       ├── respond_grader.py  # 6-criterion weighted scoring
│       └── thread_grader.py   # Per-step + aggregate scoring
│
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_environment.py   # Environment step/reset/state tests
│   ├── test_graders.py       # Grader determinism and scoring tests
│   ├── test_server.py        # API endpoint tests
│   └── test_inference.py     # Inference output format tests
│
└── frontend/                 # Optional React visualization
    └── mini-rl-environment.jsx
```

## 🚀 Quick Start

```bash
# 1. Clone/navigate to the project
cd my_env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run validation (checks everything before submission)
python validate.py

# 4. Run tests
pytest tests/ -v

# 5. Start the server
python -m uvicorn src.server:app --host 0.0.0.0 --port 7860

# 6. Test the API
curl http://localhost:7860/
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d '{"task_id":"email_classify"}'
```

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built for the **Meta x Hugging Face OpenEnv Hackathon** (April 2026).

---

<p align="center">
  <i>Simulating real-world email triage tasks for AI agent training</i>
</p>
