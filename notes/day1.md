# Day 1 — Foundations

## Core concept of the day: Workflow vs Agent

A workflow uses LLMs but the control flow is fixed in code. The engineer decided
in advance what would happen at each step. The LLM is a smart string-to-string
function inside a pipeline.

An agent inverts this. The LLM gets to decide what happens next. It picks the
tool, decides when it has enough information, chooses to stop. The control flow
itself is a runtime decision.

Why this matters: agents are more powerful but also more failure-prone. They
loop, they call tools incorrectly, they hallucinate goals, they cost more per
task. Most production AI systems are better served by workflows. Agents earn
their place only when the task genuinely requires runtime adaptation.

## My own examples

A workflow I've built: FLIK Survey Intelligence. Intent classifier routes
queries, then a fixed retrieval-then-generation pipeline. The LLM doesn't decide
to do anything different based on what it sees. That's a workflow, not an agent,
and it's the right design for that problem.

What FLIK would look like as an agent: an LLM that decides whether to query
Snowflake, search documents, or escalate to a human, then loops until confident.
For FLIK that would be overkill. The five query patterns are well-defined.
Workflow wins.

A real agent use case: research. The system can't know in advance whether to
search the web, read PDFs, run Python, or refine its query, because the right
path depends on what it discovers along the way. Atlas is genuinely an agent
because research genuinely requires runtime adaptation.

## The augmented LLM

Three components: retrieval (look things up), tools (do things), memory
(remember). Atlas will have all three by end of Week 1.

## Open questions I'm holding

1. When does multi-agent actually beat single-agent? Hypothesis: when sub-tasks
   are parallel-izable or require different specializations.
2. How do I evaluate an agent's *trajectory* (the sequence of decisions) vs just
   its final output? This is Day 15-16 work but worth noting now.
3. What's the right unit of failure recovery — the whole agent, or a single
   tool call?

## What I'm building toward

By end of Week 1, Atlas has a ReAct loop, real tool use, structured outputs,
and LangGraph-based orchestration with Postgres persistence.

By end of Week 2, it's multi-agent with parallel sub-agent fan-out, MCP tool
integration, and human-in-the-loop checkpoints.

By end of Week 3, it has a real eval harness, hallucination detection, full
observability, and cost/safety guardrails.

By end of Week 4, it's deployed and demo-ready.

## LinkedIn post draft (for Day 7)

Theme: "Most production AI isn't agents. And that's correct."

Hook: Most teams calling their systems "agents" are shipping workflows. Here's
why the distinction matters.