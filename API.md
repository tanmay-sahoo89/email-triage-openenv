# Email Triage OpenEnv - API Reference

## Core OpenEnv Endpoints

All core endpoints follow the OpenEnv HTTP specification.

### `GET /`

**Health Check & Environment Metadata**

```bash
curl https://emitboi-email-triage-env.hf.space/
```

**Response:**

```json
{
  "name": "Email Triage Environment",
  "version": "1.3.0",
  "status": "healthy",
  "features": [
    "deterministic_grading",
    "curriculum_learning",
    "email_similarity_avoidance",
    "streaming_feedback",
    "agent_benchmarking",
    "explainable_ai",
    "adversarial_testing",
    "business_impact_metrics"
  ],
  "tasks": [
    { "id": "email_classify", "difficulty": "easy" },
    { "id": "email_respond", "difficulty": "medium" },
    { "id": "email_thread", "difficulty": "hard" }
  ]
}
```

---

### `POST /reset`

**Start a New Episode**

```bash
curl -X POST https://emitboi-email-triage-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "email_classify",
    "email_index": 0,
    "agent_id": "my-agent-v1",
    "adversarial_mode": false
  }'
```

**Parameters:**

- `task_id` (string, optional): Task to run (`email_classify`, `email_respond`, `email_thread`). Default: curriculum-based selection.
- `email_index` (integer, optional): Specific email index (0-based). Default: random.
- `agent_id` (string, optional): Agent identifier for benchmarking. Default: anonymous.
- `adversarial_mode` (boolean, optional): Enable adversarial testing mode. Default: false.

**Response:**

```json
{
  "task_id": "email_classify",
  "task_name": "Email Classification",
  "difficulty": "easy",
  "step": 1,
  "max_steps": 1,
  "prompt": "Classify this email by priority and category:\n\nFrom: customer@example.com\nSubject: Payment Failed\n\nMy payment was declined...",
  "email_data": {
    "id": "email_001",
    "sender": "customer@example.com",
    "subject": "Payment Failed",
    "body": "My payment was declined...",
    "is_phishing": false,
    "emotional_escalation": false
  },
  "curriculum_info": {
    "unlocked_tasks": ["email_classify"],
    "next_task": "email_respond",
    "progress": 0.45
  }
}
```

---

### `POST /step`

**Execute an Action**

```bash
curl -X POST https://emitboi-email-triage-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Priority: urgent\nCategory: billing",
    "agent_id": "my-agent-v1"
  }'
```

**Parameters:**

- `message` (string): Agent action/response.
- `agent_id` (string, optional): Agent identifier for benchmarking.
- `tool_calls` (array, optional): Structured tool-calling payload.

**Response:**

```json
{
  "observation": {
    "task_id": "email_classify",
    "step": 1,
    "max_steps": 1,
    "prompt": "..."
  },
  "reward": 0.95,
  "done": true,
  "info": {
    "grading_details": {
      "priority_correct": true,
      "category_correct": true,
      "phishing_bonus": 0.0,
      "criterion_scores": { "priority": 0.5, "category": 0.5 }
    },
    "explanation": "✅ Correctly classified both priority and category.",
    "curriculum_info": {
      "episode_avg": 0.95,
      "task_progress": 0.45,
      "next_unlock_threshold": 0.75
    }
  }
}
```

---

### `GET /state`

**Get Current Episode State**

```bash
curl https://emitboi-email-triage-env.hf.space/state
```

**Response:**

```json
{
  "task_id": "email_classify",
  "step": 1,
  "max_steps": 1,
  "episode_rewards": [0.95],
  "episode_avg_reward": 0.95,
  "done": true,
  "email_data": {...},
  "curriculum_info": {
    "unlocked_tasks": ["email_classify"],
    "task_mastery": {
      "email_classify": {"episodes": 5, "avg_reward": 0.88},
      "email_respond": {"episodes": 0, "avg_reward": 0.0}
    }
  }
}
```

---

## Analytics & Metrics Endpoints (NEW)

### `GET /metrics/performance`

**Get Real-Time Performance Metrics**

```bash
curl https://emitboi-email-triage-env.hf.space/metrics/performance?task_id=email_classify
```

**Parameters:**

- `task_id` (string, optional): Specific task. Default: all tasks.

**Response:**

```json
{
  "task_id": "email_classify",
  "stats": {
    "total_episodes": 125,
    "total_successes": 110,
    "avg_reward": 0.85,
    "success_rate": 0.88,
    "min_reward": 0.01,
    "max_reward": 1.0,
    "avg_steps": 1.0,
    "improvement_trend": 0.08
  },
  "learning_curve": [0.72, 0.74, 0.76, 0.79, 0.82, 0.85],
  "anomalies_detected": [
    {
      "episode_index": 42,
      "reward": 0.05,
      "z_score": 2.8,
      "type": "low"
    }
  ],
  "learning_quality": "excellent"
}
```

---

### `POST /benchmark/compare`

**Compare Multiple Agents**

```bash
curl -X POST https://emitboi-email-triage-env.hf.space/benchmark/compare \
  -H "Content-Type: application/json" \
  -d '{
    "agent_ids": ["agent-gpt4", "agent-claude", "agent-qwen"]
  }'
```

**Response:**

```json
{
  "timestamp": "2025-04-11T14:44:55.808Z",
  "agents": {
    "agent-gpt4": {
      "agent_id": "agent-gpt4",
      "model_name": "GPT-4",
      "task_scores": {
        "email_classify": {
          "avg_reward": 0.92,
          "episodes": 50,
          "vs_baseline": 0.0
        },
        "email_respond": {
          "avg_reward": 0.88,
          "episodes": 50,
          "vs_baseline": 0.03
        }
      },
      "overall_avg": 0.90
    },
    "agent-claude": {...},
    "agent-qwen": {...}
  }
}
```

---

### `GET /benchmark/rankings`

**Get Agent Rankings**

```bash
curl https://emitboi-email-triage-env.hf.space/benchmark/rankings?task_id=email_respond
```

**Parameters:**

- `task_id` (string, optional): Rank by specific task. Default: overall.

**Response:**

```json
{
  "task_id": "email_respond",
  "rankings": [
    { "agent_id": "agent-gpt4", "avg_reward": 0.88 },
    { "agent_id": "agent-claude", "avg_reward": 0.85 },
    { "agent_id": "agent-qwen", "avg_reward": 0.78 }
  ]
}
```

---

### `POST /agent/register`

**Register a New Agent for Benchmarking**

```bash
curl -X POST https://emitboi-email-triage-env.hf.space/agent/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent-v2",
    "model_name": "Qwen2.5-72B-Instruct"
  }'
```

**Response:**

```json
{
  "status": "success",
  "agent_id": "my-agent-v2",
  "model_name": "Qwen2.5-72B-Instruct"
}
```

---

### `GET /metrics/impact`

**Get Business Impact Metrics**

```bash
curl https://emitboi-email-triage-env.hf.space/metrics/impact
```

**Response:**

```json
{
  "impact": {
    "fraud_prevented_emails": 8,
    "fraud_prevented_value_usd": 2000,
    "customer_satisfaction_score": 0.82,
    "total_hours_saved": 12.5,
    "hours_saved_value_usd": 437.5,
    "successful_resolutions": 95,
    "resolution_rate": 0.76,
    "total_episodes": 125,
    "estimated_total_value_usd": 2437.5
  },
  "timestamp": "2025-04-11T14:44:55.808Z",
  "summary": "Prevented $2437.50 in fraud/downtime"
}
```

**Interpretation:**

- **Fraud prevented value**: Based on $250 per prevented fraud email
- **Hours saved value**: Based on $35/hour cost of manual support
- **Estimated total value**: Sum of all prevented costs (shows ROI)

---

### `GET /explain/{episode_id}`

**Get Explainability Report for an Episode**

```bash
curl https://emitboi-email-triage-env.hf.space/explain/ep_12345
```

**Response:**

```json
{
  "episode_id": "ep_12345",
  "task_id": "email_classify",
  "agent_response": "Priority: urgent\nCategory: billing",
  "final_reward": 0.95,
  "grading_criteria": {
    "priority_correct": true,
    "category_correct": true,
    "phishing_bonus": false
  },
  "why_this_score": "✅ Agent correctly classified priority and category with high confidence."
}
```

---

### `GET /recent-decisions`

**Get Most Recent Agent Decisions**

```bash
curl https://emitboi-email-triage-env.hf.space/recent-decisions?limit=5
```

**Parameters:**

- `limit` (integer, optional): Number of recent decisions to return. Default: 10.

**Response:**

```json
{
  "decisions": [
    {
      "episode_id": "ep_12345",
      "task_id": "email_classify",
      "agent_response": "Priority: urgent\nCategory: billing",
      "reward": 0.95,
      "grading_details": {...},
      "timestamp": "2025-04-11T14:44:55.808Z"
    }
  ],
  "limit": 5,
  "total_recorded": 245
}
```

---

### `POST /test/adversarial`

**Run Adversarial Testing Suite**

```bash
curl -X POST https://emitboi-email-triage-env.hf.space/test/adversarial \
  -H "Content-Type: application/json" \
  -d '{
    "num_tests": 5
  }'
```

**Parameters:**

- `num_tests` (integer, optional): Number of adversarial tests. Default: 5.

**Response:**

```json
{
  "timestamp": "2025-04-11T14:44:55.808Z",
  "tests_run": 5,
  "passed": 5,
  "failed": 0,
  "resilience_score": 1.0,
  "failed_cases": []
}
```

**Test Scenarios:**

- Subtle Phishing
- Sarcasm Detection
- Urgent but Fake
- Vague Request
- Contradictory Information

---

## Streaming Endpoints

### `POST /stream_step`

**Streaming Grading Feedback**

```bash
curl -X POST https://emitboi-email-triage-env.hf.space/stream_step \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Priority: urgent\nCategory: billing",
    "stream_interval": 0.1,
    "agent_id": "my-agent"
  }'
```

Streams Server-Sent Events (SSE) with partial grading updates.

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad request (invalid parameters)
- **404**: Resource not found
- **500**: Server error

**Error Response:**

```json
{
  "detail": "Error description"
}
```

---

## Rate Limiting & Deployment

- **No rate limiting** for local/development deployments
- **HF Spaces**: Follow HF rate limiting policy
- **Docker**: Runs on port 7860

---

## Examples

### Example 1: Complete Episode

```bash
# Reset
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "email_classify", "agent_id": "test-agent"}'

# Classify
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"message": "Priority: urgent\nCategory: billing"}'

# Get metrics
curl http://localhost:7860/metrics/performance?task_id=email_classify
```

### Example 2: Benchmark Two Agents

```bash
# Register agents
curl -X POST http://localhost:7860/agent/register \
  -d '{"agent_id": "agent-a", "model_name": "Model-A"}'
curl -X POST http://localhost:7860/agent/register \
  -d '{"agent_id": "agent-b", "model_name": "Model-B"}'

# Run episodes with each agent...
# Then compare
curl -X POST http://localhost:7860/benchmark/compare \
  -d '{"agent_ids": ["agent-a", "agent-b"]}'
```

### Example 3: Analyze Impact

```bash
# Run several episodes...
# Then check impact
curl http://localhost:7860/metrics/impact
```

---

## Documentation

- [GitHub Repository](https://github.com/tanmay-sahoo89/email-triage-openenv)
- [HF Space](https://huggingface.co/spaces/EmitBoi/email-triage-env)
- [OpenEnv Specification](https://github.com/meta-pytorch/OpenEnv)
