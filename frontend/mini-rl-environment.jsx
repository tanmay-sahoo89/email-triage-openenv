import { useState, useEffect, useRef, useCallback } from "react";

const API_BASE = "http://localhost:7860";

// ── API helpers ──
async function apiReset(taskId = null) {
  const body = taskId ? { task_id: taskId } : {};
  const res = await fetch(`${API_BASE}/reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function apiStep(message) {
  const res = await fetch(`${API_BASE}/step`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  return res.json();
}

async function apiState() {
  const res = await fetch(`${API_BASE}/state`);
  return res.json();
}

// ── Animated counter ──
function AnimNum({ value, decimals = 2 }) {
  const [display, setDisplay] = useState(0);
  const ref = useRef(null);
  useEffect(() => {
    let start = display;
    const diff = value - start;
    if (Math.abs(diff) < 0.001) { setDisplay(value); return; }
    const steps = 18;
    let i = 0;
    clearInterval(ref.current);
    ref.current = setInterval(() => {
      i++;
      const t = i / steps;
      const ease = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      setDisplay(start + diff * ease);
      if (i >= steps) { setDisplay(value); clearInterval(ref.current); }
    }, 22);
    return () => clearInterval(ref.current);
  }, [value]);
  return <span>{display.toFixed(decimals)}</span>;
}

const TASKS = [
  { id: "email_classify", name: "Classification", difficulty: "easy" },
  { id: "email_respond", name: "Response Drafting", difficulty: "medium" },
  { id: "email_thread", name: "Thread Resolution", difficulty: "hard" },
];

export default function MiniRLEnvironment() {
  const [selectedTask, setSelectedTask] = useState(0);
  const [response, setResponse] = useState("");
  const [observation, setObservation] = useState(null);
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [phase, setPhase] = useState("idle");
  const [error, setError] = useState(null);

  const task = TASKS[selectedTask];

  const handleReset = useCallback(async (taskId) => {
    setPhase("loading");
    setError(null);
    try {
      const obs = await apiReset(taskId || task.id);
      setObservation(obs);
      setResults(null);
      setResponse("");
      setPhase("ready");
    } catch (e) {
      setError(`Failed to connect to backend: ${e.message}`);
      setPhase("error");
    }
  }, [task]);

  const handleStep = useCallback(async () => {
    if (!response.trim()) return;
    setPhase("grading");
    try {
      const result = await apiStep(response);
      setResults(result);
      setObservation(result.observation);
      setHistory((h) => [{ task: task.name, reward: result.reward, done: result.done }, ...h].slice(0, 10));
      setPhase(result.done ? "done" : "ready");
      if (!result.done) setResponse("");
    } catch (e) {
      setError(`Step failed: ${e.message}`);
      setPhase("error");
    }
  }, [response, task]);

  return (
    <div style={{
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      background: "#0a0a0f", color: "#e0e0e8",
      minHeight: "100vh", padding: 0, position: "relative", overflow: "hidden",
    }}>
      <div style={{
        position: "fixed", inset: 0, zIndex: 0, opacity: 0.04,
        backgroundImage: "linear-gradient(#3af 1px, transparent 1px), linear-gradient(90deg, #3af 1px, transparent 1px)",
        backgroundSize: "40px 40px",
      }} />

      <div style={{ position: "relative", zIndex: 1, maxWidth: 900, margin: "0 auto", padding: "24px 16px 60px" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            display: "inline-block", padding: "3px 14px",
            border: "1px solid #3af3", borderRadius: 2,
            fontSize: 10, letterSpacing: 4, color: "#3af", textTransform: "uppercase", marginBottom: 10,
          }}>openenv environment</div>
          <h1 style={{
            fontSize: 28, fontWeight: 700, margin: "8px 0 6px",
            background: "linear-gradient(135deg, #3af, #a78bfa, #f472b6)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          }}>Email Triage & Response</h1>
          <p style={{ color: "#888", fontSize: 12, margin: 0 }}>
            Classify emails, draft responses, resolve threads. You are the agent.
          </p>
        </div>

        {/* Task Selector */}
        <div style={{ marginBottom: 20 }}>
          <label style={{ fontSize: 10, letterSpacing: 2, color: "#666", textTransform: "uppercase", display: "block", marginBottom: 8 }}>
            Select Task
          </label>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {TASKS.map((t, i) => (
              <button key={t.id} onClick={() => { setSelectedTask(i); handleReset(t.id); }} style={{
                background: i === selectedTask ? "linear-gradient(135deg, #3af2, #a78bfa22)" : "#14141f",
                border: `1px solid ${i === selectedTask ? "#3af" : "#2a2a3a"}`,
                color: i === selectedTask ? "#3af" : "#888",
                borderRadius: 4, padding: "8px 14px", fontSize: 11,
                fontFamily: "inherit", cursor: "pointer",
              }}>
                {t.name} ({t.difficulty})
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div style={{ background: "#2a1015", border: "1px solid #fb7185", borderRadius: 6, padding: 16, marginBottom: 16, color: "#fb7185", fontSize: 12 }}>
            {error}
            <div style={{ marginTop: 8, color: "#888", fontSize: 11 }}>
              Make sure the Python backend is running: <code>uvicorn src.server:app --port 7860</code>
            </div>
          </div>
        )}

        {/* Observation */}
        {observation && (
          <div style={{
            background: "#12121e", border: "1px solid #1e1e30", borderRadius: 6,
            padding: "16px 20px", marginBottom: 16,
          }}>
            <div style={{ fontSize: 10, color: "#666", letterSpacing: 2, textTransform: "uppercase", marginBottom: 8 }}>
              Observation (Step {observation.step + 1}/{observation.max_steps})
            </div>
            <pre style={{ margin: 0, fontSize: 12, color: "#c8c8d4", lineHeight: 1.6, whiteSpace: "pre-wrap", fontFamily: "inherit" }}>
              {observation.prompt}
            </pre>
          </div>
        )}

        {/* Agent Response */}
        <div style={{ marginBottom: 16 }}>
          <textarea
            value={response} onChange={(e) => setResponse(e.target.value)}
            placeholder="Type your response here..."
            rows={4}
            style={{
              width: "100%", background: "#0e0e18", border: "1px solid #2a2a3a",
              borderRadius: 6, color: "#e0e0e8", padding: "12px 14px", fontSize: 13,
              fontFamily: "inherit", resize: "vertical", outline: "none", boxSizing: "border-box",
            }}
          />
        </div>

        {/* Actions */}
        <div style={{ display: "flex", gap: 10, marginBottom: 28 }}>
          <button onClick={handleStep} disabled={phase === "grading" || !response.trim()} style={{
            background: phase === "grading" ? "#2a2a3a" : "linear-gradient(135deg, #3af, #818cf8)",
            color: "#fff", border: "none", borderRadius: 5, padding: "10px 24px",
            fontSize: 12, fontFamily: "inherit", cursor: "pointer", fontWeight: 600,
            opacity: !response.trim() ? 0.4 : 1,
          }}>
            {phase === "grading" ? "Evaluating..." : "Submit Action"}
          </button>
          <button onClick={() => handleReset()} style={{
            background: "none", color: "#666", border: "1px solid #2a2a3a",
            borderRadius: 5, padding: "10px 18px", fontSize: 12, fontFamily: "inherit", cursor: "pointer",
          }}>
            New Episode
          </button>
        </div>

        {/* Results */}
        {results && (
          <div style={{ animation: "fadeSlide .35s ease" }}>
            <div style={{
              background: "linear-gradient(135deg, #12121e, #1a1a2e)", border: "1px solid #2a2a3a",
              borderRadius: 8, padding: 24, textAlign: "center", marginBottom: 20,
            }}>
              <div style={{ fontSize: 10, letterSpacing: 3, color: "#666", textTransform: "uppercase", marginBottom: 4 }}>
                Step Reward
              </div>
              <div style={{
                fontSize: 52, fontWeight: 700,
                color: results.reward > 0.7 ? "#3af" : results.reward > 0.4 ? "#fbbf24" : "#fb7185",
              }}>
                <AnimNum value={results.reward} />
              </div>
              <div style={{ fontSize: 11, color: "#666", marginTop: 6 }}>/ 1.00</div>
              {results.done && (
                <div style={{ fontSize: 12, color: "#34d399", marginTop: 8 }}>Episode Complete</div>
              )}
            </div>

            {/* Reward breakdown */}
            {results.info?.reward_detail?.breakdown && (
              <div style={{ background: "#12121e", border: "1px solid #1e1e30", borderRadius: 6, padding: 16, marginBottom: 20 }}>
                <div style={{ fontSize: 10, letterSpacing: 2, color: "#a78bfa", textTransform: "uppercase", marginBottom: 12 }}>
                  Score Breakdown
                </div>
                {Object.entries(results.info.reward_detail.breakdown).map(([key, val]) => (
                  <div key={key} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: "1px solid #1a1a2a" }}>
                    <span style={{ fontSize: 11, color: "#aaa" }}>{key}</span>
                    <span style={{ fontSize: 11, color: val >= 0.7 ? "#34d399" : val >= 0.4 ? "#fbbf24" : "#fb7185", fontWeight: 600 }}>
                      {(val * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
                {results.info.reward_detail.feedback && (
                  <div style={{ marginTop: 8, fontSize: 11, color: "#888" }}>
                    {results.info.reward_detail.feedback}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* History */}
        {history.length > 0 && (
          <div style={{ background: "#12121e", border: "1px solid #1e1e30", borderRadius: 6, padding: "16px 20px" }}>
            <div style={{ fontSize: 10, letterSpacing: 2, color: "#666", textTransform: "uppercase", marginBottom: 12 }}>
              Episode History
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {history.map((h, i) => (
                <div key={i} style={{ background: "#0e0e18", borderRadius: 4, padding: "8px 12px", minWidth: 90 }}>
                  <div style={{ fontSize: 10, color: "#888", marginBottom: 4 }}>{h.task}</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: h.reward > 0.7 ? "#3af" : h.reward > 0.4 ? "#fbbf24" : "#fb7185" }}>
                    {h.reward.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeSlide { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
        textarea::placeholder { color: #444; }
        * { box-sizing: border-box; }
        button:hover { filter: brightness(1.15); }
      `}</style>
    </div>
  );
}
