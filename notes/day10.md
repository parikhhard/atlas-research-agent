# Day 10 — Short-Term Memory and Context Window Management

## Core insight

Context is a finite, expensive resource that has to be actively managed.
Most agent demos work because the conversations are short. Production
agents fail at turn 20 not because the model is bad but because the
context has grown unboundedly. Three things go wrong simultaneously:
cost scales linearly with conversation length, latency scales linearly,
and the model gets worse at attending to relevant information.

The discipline of short-term memory is the discipline of deciding what
to keep verbatim, what to summarize, and what to drop.

## Why summarization beat the alternatives

Three strategies on the table:

1. Sliding window. Drop old messages entirely. Simple but lossy.
2. Summarization. Compress older messages into a summary. Costs one
   extra LLM call per compaction but preserves continuity.
3. Selective retention. Keep some verbatim, summarize some, drop
   some. Higher quality but harder to tune.

I picked summarization because it sits in the middle. The cost is one
extra LLM call per compaction event, which happens maybe every 5-10
turns. That's a tiny overhead relative to the agent calls themselves,
and the user gets a system that meaningfully remembers prior context
even at turn 30.

Sliding window would have been simpler to implement but the trade
isn't worth it for a research agent where users follow up on earlier
findings. Selective retention is the next evolution but introduces
tuning complexity I didn't want to take on in one day.

## The RemoveMessage pattern is the underrated framework feature

Before today I'd been treating the messages list as append-only. That's
fine for sequential conversations but breaks the moment you need to
edit history. LangGraph's RemoveMessage is what makes editing safe.

The pattern: return a list of RemoveMessage objects to delete, plus new
messages to add, in a single state update. The framework processes the
removes first, then the adds. Net effect: surgical edits to message
history.

This is the framework giving me a primitive I'd have struggled to build
myself. Anyone who's tried to do this with raw lists has probably hit
the bugs where a parallel update overwrites the edit.

## The compactor node is a graph node, not a hook

I considered making compaction a wrapper around the agent node, like a
decorator. That would have worked but it would have hidden the
compaction logic from the graph's observability. Anyone looking at the
graph would have seen "agent" and not known about the silent compaction
happening before each invocation.

Making it an explicit node means:

- Traces show compaction events as their own step
- Checkpoints capture pre-compaction and post-compaction states separately
- Anyone reading the graph code understands the flow immediately

The principle: when a system does something important, make it visible
in the architecture. Hidden behavior is a debugging burden later.

## Tuning the threshold

I set the threshold at 8000 tokens with 6 recent messages always kept
verbatim. Those numbers are tuned for the conversations Atlas handles
right now. They're not universal.

The right way to think about tuning:

- Threshold too low → compacting constantly, wasting summary calls
- Threshold too high → context grows large, costs and latency rise
- Recent message buffer too small → compaction kicks in but the agent
  loses immediate context
- Recent message buffer too large → compaction barely reduces context

The right answer is empirical. Observe real conversations, find the
elbow where context starts mattering for the model's behavior, set
threshold just below it.

## What I'm holding for later

1. Long-term memory is a different beast. Today's compaction is about
   surviving the current conversation. Long-term memory is about
   recalling things from prior conversations. That's Day 11 (vector
   recall).

2. Selective retention would beat summarization on a quality-per-token
   basis. The framework: keep the user's original question forever,
   keep the latest 5 messages verbatim, summarize everything else.
   Worth experimenting with in Week 4 polish.

3. The summary itself can drift. If you summarize a summary five times,
   information decays. A production system needs a strategy for
   re-anchoring (going back to the original messages occasionally).
   This is the "lossy compression" problem and there isn't a clean
   answer yet.

## The interview answer

"How do you handle context window management in long-running agent
conversations?"

Threshold-based summarization compaction. When the conversation crosses
a token threshold, an explicit graph node summarizes older messages
into a compact representation and replaces them in state. Recent
messages stay verbatim so the agent always has immediate context.
LangGraph's RemoveMessage primitive lets me edit message history
surgically without parallel-write conflicts.

The reason this matters: without compaction, every multi-turn agent
conversation eventually hits context window limits, cost spirals, and
model attention degrades. With it, the same agent can hold 30+ turn
conversations without any of those failure modes.

## LinkedIn post angle

"Most multi-turn agent demos work because the conversation is short.
At turn 20, every production agent has the same problem: context has
grown unboundedly, cost has spiraled, and the model is forgetting
what the user originally asked. The unsexy fix is short-term memory
management. Here's the pattern I use."