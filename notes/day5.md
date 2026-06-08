# Day 5 — LangGraph Fundamentals

## Core insight

The hand-rolled while loop and the LangGraph state graph are the same thing.
The graph just makes the control flow data instead of code.

In the loop version, the "should we continue" logic was a python if statement
inside the while. In the graph version, it's a function attached to a
conditional edge. Same logic, different location. The relocation matters
because once control flow is data, you can add persistence, branching,
interrupts, and observability hooks by decorating the graph instead of
rewriting the loop.

## What I actually learned by building both

Frameworks are most valuable for the changes you haven't made yet. Today's
LangGraph version does nothing the hand-rolled loop didn't already do. The
payoff arrives on Day 6 when I add Postgres checkpointing without rewriting
the agent, and again on Day 11 when I add memory, and again on Days 8 and 9
when multi-agent orchestration enters. Every one of those will be a
decoration on the existing graph, not a rewrite.

The discipline of building it by hand first paid off. I now know what the
framework is abstracting. When LangGraph does something I don't understand,
my first reaction isn't to read documentation. It's to ask which part of my
hand-rolled loop corresponds. That mental map is the difference between
operating a framework and being able to rebuild it.

## What LangGraph solves and what it doesn't

Solves: state management, branching, persistence hooks (Day 6), composability
across nodes, observability instrumentation points.

Does not solve: tool design, system prompt design, eval design, hallucination
detection, cost optimization, failure mode handling for specific tools.

The hard parts of agent engineering are still mine to own. The framework
saves me from rewriting the loop every time I want a new behavior.

## The interview answer

"I built the ReAct loop by hand first, then moved to LangGraph deliberately.
The framework gives me state management, branching, persistence hooks, and
observability instrumentation points that I'd otherwise rewrite for every
new feature. What it doesn't solve is the actual hard work: tool design,
prompt design, evals, and failure modes. Those are still mine to own. I use
the framework where it removes plumbing and I keep ownership of the parts
that need engineering judgment."

That answer reflects a senior posture. Most candidates either say "I use
LangGraph" (junior) or "I build everything from scratch" (often dogmatic).
The mature answer is "I use the framework for the plumbing it solves and I
own the design decisions it doesn't solve."

## Where it gets interesting

Today the graph is two nodes. By the end of week 2 it will have a planner
node, a fan-out to multiple worker nodes, a synthesizer node, and a critic
node. The control flow will branch and reconverge. The same `compile().invoke()`
interface will run all of it. That's the payoff.

## LinkedIn post draft

Theme: "Why I built the agent loop by hand before reaching for LangGraph.
Frameworks make sense after you understand what they abstract. Building
from scratch first is the cheapest way to develop the diagnostic skill of
knowing what's plumbing and what's design."