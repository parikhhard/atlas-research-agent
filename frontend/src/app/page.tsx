"use client";

import { useState, useEffect } from "react";

function newThreadId() {
  return crypto.randomUUID();
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("fast");
  const [threadId, setThreadId] = useState(null);
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
  setThreadId(newThreadId());
}, []);

  async function handleSubmit() {
    if (!query.trim()) return;
    const userTurn = { role: "user", content: query };
    setConversation((prev) => [...prev, userTurn]);
    setQuery("");
    setLoading(true);
    
    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, mode, engine: "graph", thread_id: threadId }),
      });
      const data = await res.json();
      const agentTurn = {
        role: "agent",
        content: data.answer,
        trace: data.trace,
        iterations: data.iterations,
      };
      setConversation((prev) => [...prev, agentTurn]);
    } catch {
      setConversation((prev) => [...prev, { role: "agent", content: "Error" }]);
    } finally {
      setLoading(false);
    }
  }

  function startNewThread() {
    setThreadId(newThreadId());
    setConversation([]);
  }

  return (
    <main>
      <h1>Atlas</h1>
      <p>A multi-agent research system. Day 6 — persistent state.</p>

      <div>
        <label>
          Mode:{" "}
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="fast">Fast</option>
            <option value="thorough">Thorough</option>
          </select>
        </label>{" "}
        <button onClick={startNewThread}>New Conversation</button>
      </div>

      <div>
        <small>Thread: {threadId}</small>
      </div>

      <hr />

      <div>
        <h2>Conversation</h2>
        {conversation.map((turn, i) => (
          <div key={i}>
            <strong>{turn.role.toUpperCase()}:</strong> {turn.content}
            {turn.trace && (
              <details>
                <summary>Trace ({turn.iterations} steps)</summary>
                {turn.trace.map((step, j) => (
                  <div key={j}>
                    <strong>{step.step}:</strong>{" "}
                    {step.tool ? `${step.tool}(${JSON.stringify(step.input)})` : step.content}
                  </div>
                ))}
              </details>
            )}
          </div>
        ))}
      </div>

      <div>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask Atlas something..."
          rows={3}
        />
        <br />
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </main>
  );
}