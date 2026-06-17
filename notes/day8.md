# Day 8 — The Orchestrator-Worker Pattern

## Core insight

Multi-agent isn't fancier than single-agent. It's a different tool for a
different problem. Single-agent ReAct compresses everything into one
growing conversation. Orchestrator-worker decomposes the problem into
focused sub-tasks, each with its own context window, then reconciles.

The right question isn't "should I use multi-agent?" The right question is
"does this task have independent parallelizable sub-parts whose contexts
shouldn't pollute each other?"

If yes, multi-agent earns its cost.
If no, single-agent is cheaper, faster, and just as good.

## The three-node decomposition

Today's architecture is the simplest useful multi-agent pattern:

- A planner that decomposes
- N workers, each focused on one sub-task
- A synthesizer that combines

This is structured multi-agent. The orchestrator (planner + synthesizer)
is explicit. The workers are stateless and specialized. The control flow
is a graph I designed, not a free-for-all between agents.

Most production multi-agent systems converge on this shape because it's
debuggable. You can inspect the planner's decomposition, look at each
worker's answer independently, and check the synthesizer's reasoning.
That's three places to debug, not one tangled conversation.

## What I noticed building it

The planner over-decomposes when the query is simple. Asked "what is the
population of Tokyo?" it sometimes still returns one sub-task that's
identical to the query. That's fine - we just pay one extra LLM call.

The planner under-decomposes when the query is genuinely complex. Asked
"compare populations and economies of Tokyo and NYC" it sometimes
returned 2 sub-tasks instead of 4. Prompt tuning would fix this.

The workers do better on focused questions than the single agent does on
the same question embedded in a bigger context. That's the context window
dividend: a focused worker with 5 iterations of context is more accurate
than one agent with 30 iterations of mixed context.

The synthesizer is the hardest node to evaluate. It can hallucinate
combinations of worker outputs that weren't actually in any worker's
answer. This is a Day 17 problem (critic agents).

## The cost analysis

For a simple query (one fact):
- Single-agent: 2 LLM calls (one to use tool, one to summarize)
- Multi-agent: 3 LLM calls (planner + worker + synthesizer)
- Multi-agent is 50% more expensive for no benefit.

For a complex comparison (3 facts):
- Single-agent: 4-6 LLM calls in one growing conversation
- Multi-agent: 5 LLM calls (planner + 3 workers + synthesizer)
- Roughly the same total calls, but multi-agent answers are higher quality
  because each worker had a clean context.

The economics flip when:
- The task has 3+ genuinely independent parts
- The single-agent context would grow past ~30k tokens
- The sub-tasks could run in parallel (Day 9 unlocks this)
- Different sub-tasks need different prompts or tools

## When orchestrator-worker is wrong

Three cases I'd push back on:

1. The query is one fact. Just use a single agent.
2. The sub-tasks need to share state (one builds on another). Multi-agent
   isolation hurts you here. Use a single agent or sequential workflow.
3. The decomposition itself is the answer (e.g., "give me a research plan
   for X"). The planner alone is the deliverable; no workers needed.

## The interview answer

"How do you decide between single-agent and multi-agent?"

Single-agent ReAct compresses the whole task into one growing
conversation. Multi-agent (orchestrator-worker) decomposes into focused
sub-tasks with isolated contexts. I use multi-agent when the task has
three or more independent parts, when single-agent context would explode
past 30k tokens, or when sub-tasks would benefit from different prompts
or tools.

For simple queries I default to single-agent because multi-agent is 50%
more expensive for no benefit. The decomposition has to earn its cost.

## Where this is going

Tomorrow (Day 9): parallel workers. Right now workers run sequentially,
which means a 3-sub-task query takes 3x longer than necessary. Running
workers in parallel cuts latency dramatically. This is the moment
multi-agent actually beats single-agent on wall-clock time, not just
quality.

Day 10 to 14: memory and coordination. Workers right now are stateless.
That's correct for parallel research but wrong for tasks where one
worker's output feeds another. Week 2 closes by adding the patterns for
both isolated and shared multi-agent state.

## LinkedIn post angle

"Most teams reach for multi-agent because it sounds fancier. The
question they should be asking: does my task have independent sub-parts
whose contexts shouldn't pollute each other? If yes, multi-agent earns
its cost. If no, single-agent is cheaper and just as good. Here's the
diagnostic I use."