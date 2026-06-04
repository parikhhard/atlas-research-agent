# Atlas — A Multi-Agent Research System

A production-grade multi-agent research agent. Plans, dispatches parallel
sub-agents, persists state across sessions, detects hallucinations via critic
agents, exposes every decision through observability traces.

Built over 30 days in public as a deep dive into production agent engineering.

## Stack

- Backend: Python 3.12, FastAPI, uv
- Model: Anthropic Claude (Sonnet)
- Orchestration: LangGraph (Week 1)
- State: Postgres via Supabase (Week 1)
- Observability: LangSmith (Week 3)
- Tools: MCP servers (Week 2)
- Frontend: Next.js 14 + TypeScript + shadcn/ui

## Day log

- **Day 1 — Foundations.** Project skeleton up. FastAPI backend with a thin
  Claude wrapper. Next.js frontend with one query endpoint working end-to-end.
  Internalized the workflow-vs-agent distinction. Tomorrow: implement the ReAct
  loop from scratch.

- **Day 2 — The ReAct Loop.** Built a hand-rolled ReAct loop in pure Python.
  Added web search via Tavily. The agent now decides when to search, when to
  answer directly, and when it has enough information to stop. Frontend shows
  the full reasoning trace. No framework yet, just the bare pattern.

- **Day 3 — Native tool use & multi-tool agents.** Restructured tools into a
  registry pattern. Added calculator, URL fetch, and current time tools.
  Atlas now handles multi-tool reasoning chains (search both populations, then
  calculate the ratio). Spent real time tuning tool descriptions to shape
  agent behavior. Tool design is harder than prompting, confirmed.