"use client";

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("fast");
  const [singleResult, setSingleResult] = useState(null);
  const [compareResult, setCompareResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function runSingle() {
    if (!query.trim()) return;
    setLoading(true);
    setSingleResult(null);
    setCompareResult(null);
    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, mode }),
      });
      const data = await res.json();
      setSingleResult(data);
    } catch {
      setSingleResult({ answer: "Error. Is the API running?", trace: [], iterations: 0 });
    } finally {
      setLoading(false);
    }
  }

  async function runCompare() {
    if (!query.trim()) return;
    setLoading(true);
    setSingleResult(null);
    setCompareResult(null);
    try {
      const res = await fetch("http://localhost:8000/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setCompareResult(data);
    } catch {
      setCompareResult({ fast: { answer: "Error" }, thorough: { answer: "Error" } });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Atlas</h1>
      <p>A multi-agent research system. Day 4 — system prompts as architecture.</p>

      <div>
        <h2>Ask Atlas</h2>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What would you like to research?"
          rows={4}
        />
        <br />
        <label>
          Mode:{" "}
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="fast">Fast</option>
            <option value="thorough">Thorough</option>
          </select>
        </label>
        <br />
        <button onClick={runSingle} disabled={loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>{" "}
        <button onClick={runCompare} disabled={loading}>
          {loading ? "Thinking..." : "Compare Both Modes"}
        </button>
      </div>

      {singleResult && (
        <div>
          <h2>Result ({singleResult.mode}, {singleResult.iterations} iterations)</h2>
          <h3>Answer</h3>
          <p>{singleResult.answer}</p>
          <h3>Trace</h3>
          {singleResult.trace.map((step, i) => (
            <div key={i}>
              <strong>{step.step.toUpperCase()}:</strong>{" "}
              {step.tool ? (
                <span>{step.tool}({JSON.stringify(step.input)})</span>
              ) : (
                <span>{step.content}</span>
              )}
            </div>
          ))}
        </div>
      )}

      {compareResult && (
        <div>
          <h2>Side by Side Comparison</h2>
          <div>
            <h3>Fast Mode ({compareResult.fast.iterations} iterations)</h3>
            <p>{compareResult.fast.answer}</p>
          </div>
          <hr />
          <div>
            <h3>Thorough Mode ({compareResult.thorough.iterations} iterations)</h3>
            <p>{compareResult.thorough.answer}</p>
          </div>
        </div>
      )}
    </main>
  );
}