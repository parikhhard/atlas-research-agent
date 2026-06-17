# Day 9 — Parallel Sub-Agent Fan-Out

## Core insight

Multi-agent without parallelism pays the overhead without claiming the
dividend. Sequential workers cost more LLM calls than single-agent for the
same query, AND they take the same wall-clock time. That's the worst of
both worlds.

Parallelism is what makes multi-agent worth doing. Same cost as sequential,
same quality, but workers run simultaneously. A 3-sub-task query that took
15 seconds yesterday takes 5 seconds today. The user-perceived latency is
linearly inversely proportional to the number of independent sub-tasks.

## The Send API is the right abstraction

I could have written parallel workers myself with asyncio.gather. The
reason LangGraph's Send is the right call:

1. Integrates with the graph's state management. Parallel branches flow
   through state, reducers handle the merge.
2. Integrates with the checkpointer. Each parallel branch is captured in
   the checkpoint history.
3. Integrates with eventual tracing (Day 18). Each Send becomes a
   distinct trace.
4. Doesn't require me to think about coroutines, scheduling, or
   exception handling at the asyncio level. LangGraph does it.

The cost is the framework dependency. The value is everything above.

## State reducers are the underrated concept

Before today I'd never explicitly used Annotated[list, add] in LangGraph.
With sequential workers I didn't need to. With parallel workers it's the
difference between working correctly and silently dropping 2/3 of your
results.

The mental model: any state field that gets written by multiple parallel
nodes needs an explicit reducer telling the framework how to merge. Lists
get add (concatenation). Sets could get union. Custom reducers for custom
merge logic.

This is a framework-specific concept but it generalizes. Any concurrent
system that mutates shared state has to answer "how do writes merge?" In
LangGraph the answer is reducers. In CRDTs it's merge functions. In
databases it's transaction isolation. Same question, different answers.

## What I noticed running it

For single-task queries, parallel and sequential are identical. There's
no parallelism opportunity. Multi-agent overhead is pure cost here.

For 3-task queries, the parallel version felt qualitatively different.
The answer arrived in roughly the time of the slowest single worker, not
the sum of three workers. That's the latency dividend made visible.

The synthesizer still takes its 2-3 seconds at the end. That's a
constant. It doesn't parallelize because synthesis requires all worker
outputs. This is why the latency win is sub-linear at the macro level
even though it's linear at the worker level.

## The new failure mode

Today introduced one new problem: parallel worker errors. If 2 of 3
workers succeed and 1 fails (Tavily rate limit, network blip, malformed
output), the synthesizer sees mixed results. Right now it tries to
synthesize anyway, which sometimes produces partial answers and
sometimes hallucinated combinations.

This is a Day 17 problem (critic agents) and a Day 19 problem (failure
modes). For now, partial synthesis with no retry is the simplest
behavior. In production I'd add per-worker retry with backoff and a
threshold for "if N of 3 workers fail, fail the whole query."

## The interview answer

"How do you handle parallel execution in agent systems?"

LangGraph's Send API dispatches parallel work as part of the graph
itself. A conditional edge returns a list of Sends, each one routes to
the same worker node with different input. State reducers (operator.add
on list fields) handle parallel writes. The framework handles scheduling
and convergence.

The reason this matters: multi-agent is only worth its overhead if you
use parallelism. Sequential multi-agent costs more than single-agent
for the same wall-clock latency. Parallel multi-agent costs the same
but compresses latency linearly with the number of independent sub-tasks.

## What I'm carrying into the rest of Week 2

The pattern from today (planner -> parallel workers -> synthesizer)
generalizes to almost every research-like task. The remaining Week 2
days build on this:

- Day 10: Short-term memory. How does context flow through a parallel
  multi-agent system without explosion?
- Day 11: Long-term memory. Workers are stateless today, but production
  systems need them to recall prior research.
- Day 12: MCP. The tools workers use should be reusable outside the
  agent loop, which means external tool servers.
- Day 13: Human-in-the-loop. Where do approval gates fit when N workers
  are running in parallel?
- Day 14: Agent-to-agent. What if workers genuinely need to share state
  during execution, not just at the synthesis step?

By end of Week 2 Atlas demonstrates production-grade multi-agent with
memory, MCP, and approval flows. That's portfolio material any senior
engineering team will take seriously.

## LinkedIn post angle

"Most multi-agent demos don't parallelize. They orchestrate. Worker 1,
then worker 2, then worker 3, then synthesize. That's strictly worse
than single-agent ReAct because you pay the orchestrator-worker
overhead AND wait for sequential execution. Parallelism is the whole
argument for multi-agent in production. Without it, you've paid the
cost without claiming the benefit."