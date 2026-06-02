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

- Day 1: Foundations, project skeleton, first Claude call.