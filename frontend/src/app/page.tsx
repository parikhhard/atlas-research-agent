"use client";

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (!query.trim()) return;
    setLoading(true);
    setAnswer("");
    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setAnswer(data.answer);
    } catch {
      setAnswer("Something went wrong. Is the API running on port 8000?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Atlas</h1>
      <p>A multi-agent research system. Day 1 — foundations.</p>

      <div>
        <h2>Ask Atlas</h2>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What would you like to research?"
          rows={4}
        />
        <br />
        <button
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {answer && (
        <div>
          <h2>Answer</h2>
          <p>{answer}</p>
        </div>
      )}
    </main>
  );
}