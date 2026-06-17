"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [engine, setEngine] = useState("graph");
  const [threadId, setThreadId] = useState(null);
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setThreadId(crypto.randomUUID());
  }, []);

  async function handleSubmit() {
    if (!query.trim() || !threadId) return;
    setConversation((prev) => [...prev, { role: "user", content: query }]);
    setQuery("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, engine, thread_id: threadId }),
      });
      const data = await res.json();
      setConversation((prev) => [
        ...prev,
        {
          role: "agent",
          content: data.answer,
          trace: data.trace,
          subTasks: data.sub_tasks,
        },
      ]);
    } catch {
      setConversation((prev) => [...prev, { role: "agent", content: "Error" }]);
    } finally {
      setLoading(false);
    }
  }

  function startNew() {
    setThreadId(crypto.randomUUID());
    setConversation([]);
  }

  return (
    <main>
      <h1>Atlas</h1>
      <p>A multi-agent research system. Day 8 — orchestrator-worker pattern.</p>

      <label>
        Engine:{" "}
        <select value={engine} onChange={(e) => setEngine(e.target.value)}>
          <option value="graph">Single agent (LangGraph)</option>
          <option value="multi">Multi-agent (orchestrator-worker)</option>
          <option value="react">Hand-rolled ReAct</option>
        </select>
      </label>{" "}
      <button onClick={startNew}>New Conversation</button>

      <hr />

      {conversation.map((turn, i) => (
        <div key={i}>
          <strong>{turn.role}:</strong> {turn.content}
          {turn.subTasks && turn.subTasks.length > 1 && (
            <div>
              <small>
                Decomposed into {turn.subTasks.length} sub-tasks:{" "}
                {turn.subTasks.join(" | ")}
              </small>
            </div>
          )}
        </div>
      ))}

      <hr />

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Try a comparison question like: Compare Tokyo, NYC, and London populations"
        rows={3}
      />
      <br />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Thinking..." : "Send"}
      </button>
    </main>
  );
}