"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
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
        body: JSON.stringify({ query, engine: "graph", thread_id: threadId }),
      });
      const data = await res.json();
      setConversation((prev) => [...prev, { role: "agent", content: data.answer }]);
    } catch {
      setConversation((prev) => [...prev, { role: "agent", content: "Error" }]);
    } finally {
      setLoading(false);
    }
  }

  function startNewThread() {
    setThreadId(crypto.randomUUID());
    setConversation([]);
  }

  return (
    <main>
      <h1>Atlas</h1>
      <p>A research agent with memory across turns.</p>

      <button onClick={startNewThread}>New Conversation</button>

      <hr />

      {conversation.map((turn, i) => (
        <div key={i}>
          <strong>{turn.role}:</strong> {turn.content}
        </div>
      ))}

      <hr />

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask Atlas..."
        rows={3}
      />
      <br />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Thinking..." : "Send"}
      </button>
    </main>
  );
}