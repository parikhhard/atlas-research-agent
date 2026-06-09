# Week 1 Retrospective

## What I built

Atlas, a multi tool research agent. Hand rolled ReAct loop, then ported to
LangGraph. Four tools (search, calculator, fetch, current time) with a
registry pattern and retry layer. Two prompt modes (fast, thorough) with
A/B comparison. Postgres checkpointing for persistent multi-turn conversations.
Plain Next.js frontend showing real time agent traces.

## What I learned that I didn't know on Monday

1. **Tool descriptions are prompt engineering.** The LLM reads the description
   to decide whether and how to use a tool. The "do not use for X" clause is
   the most underrated sentence in agent engineering.

2. **System prompts are architecture.** Six sections (identity, capabilities,
   behavior rules, constraints, output format, stopping conditions) deserve
   to be explicit. Most prompts collapse all six and the agent follows them
   inconsistently.

3. **State machines + checkpointers is the production agent architecture.**
   Frameworks don't give you anything magical. They give you the substrate
   to attach persistence, branching, and observability without rewriting
   the agent every time.

4. **Iterations compound cost.** Every ReAct loop is a full LLM call with
   the entire history. Most production agents I now think would be cheaper
   as workflows.

5. **The diagnostic question.** When an agent misbehaves: is this a prompt
   problem or a tool problem? That single question, applied consistently,
   fixes 80% of agent issues.

## What worked about the approach

Building the loop by hand first paid off. By the time I reached for
LangGraph I knew exactly what it was abstracting. That knowledge changes
how I read framework code and how I'd answer interview questions about
agent architecture.

Reflecting at the end of every day was unexpectedly valuable. Notes 1-7
are now interview material I can speak from. Without them I'd have built
the code and forgotten the lessons.

The mode comparison endpoint (A/B compare on the same query) became my
favorite debugging tool. Watching the same model with different prompts
produce different behavior is more instructive than reading any prompt
engineering guide.

## What I'd do differently

Spent more time than I needed fighting corporate certificate issues. In
hindsight I should have built the entire local development setup on a
personal machine and only deployed to corporate hardware. Lesson for next
time: identify environment friction early and route around it.

Got distracted by the frontend a couple times. Plain HTML is enough for
an agent demo. I don't need to think about UI until Week 4 polish.

## What I'm carrying into Week 2

Atlas can do single agent reasoning with tools and persistent memory.
Week 2 introduces:

- Orchestrator worker patterns (planner that dispatches sub agents)
- Parallel sub agent fan out
- Short and long term memory (context window strategy, vector recall)
- MCP for tool integration
- Human in the loop interrupt patterns

The hard questions I want to be able to answer by end of Week 2:

- When does multi agent beat single agent with multiple tools?
- How do you manage context windows across long conversations?
- How does MCP change tool design compared to in-process tools?
- Where do you put human approval gates without killing throughput?

## Interview readiness check

If a senior interviewer asked me right now to walk through Atlas, I could:

- Explain the workflow vs agent distinction with conviction
- Describe the ReAct loop and what each iteration costs
- Walk through tool design tradeoffs with concrete examples
- Explain why my system prompt has six sections
- Describe how LangGraph state machines plus Postgres checkpointing gives
  me persistence, multi session continuity, and auditability
- Diagnose any agent failure as a prompt issue or a tool issue
- Name the three biggest cost drivers in agent systems (iterations, tool
  calls, context length)

A week ago none of that was true. Worth noting.

## LinkedIn engagement

Posted daily this week. Today's deep post about Week 1 is intended to be
the cornerstone piece that establishes me as a serious agent engineer.

Going into Week 2 I'll continue daily, but with one big technical post
midweek as a counterweight to the day-to-day updates.