# Day 2 — The ReAct Loop From Scratch

## The core insight

An agent is a loop. Every iteration: the LLM gets the full conversation,
decides whether to use a tool or finalize an answer, and either calls the tool
or returns. The "intelligence" lives in the LLM's per-iteration decision. The
"agency" lives in the fact that we let it choose at runtime.

There is nothing else. Frameworks add ergonomics, persistence, error handling,
multi-agent coordination, observability. They do not change the core pattern.

## What I noticed building it

The first time I ran it, the agent reasoned out loud in plain text inside the
"thought" blocks: "I need to find current data, so I'll search." That text is
not for me — it's for the *next* iteration of the LLM, which will see those
words in its conversation history and use them to plan its next action. The
reasoning is not commentary. It's a working memory.

When I asked "what is 47 times 89?" the agent answered directly without
searching. When I asked "what's the latest version of Python?" it searched.
The decision boundary is whether the LLM thinks its parametric knowledge is
sufficient. That decision is fuzzy and prompt-dependent. This will be a theme
later: agent behavior is shaped by prompts more than people realize.

## Where this breaks

I tried "search for X and then search for Y based on the result." It worked
but took 3-4 iterations. Each iteration is a full LLM call with the entire
growing conversation history. Tokens scale linearly with iterations. Cost
scales linearly with iterations. Latency scales linearly with iterations.

If I were running this at production scale on long tasks, every iteration of
ReAct compounds cost. This is one of the trade-offs Anthropic's essay warned
about. Agents are expensive when they loop too much. You either cap iterations
hard, design tools that return more information per call, or fall back to a
workflow for the parts that don't need adaptive control.

## Where ReAct is the right pattern

When the next step genuinely depends on the previous observation. Research
tasks. Debugging tasks. Exploratory data analysis. Any task where you can't
write the control flow in advance because the right path is unknowable.

## Where ReAct is the wrong pattern

When the control flow IS knowable. Classification. Translation. Summarization
of a known document. Anything you could draw a flowchart for. For those, a
workflow is faster, cheaper, more reliable.

## What I'm holding for later

1. How do I handle tool failures? Right now if Tavily returns an error, the
   agent might loop on it. (Day 19 problem.)
2. How do I prevent infinite loops if the LLM keeps wanting to search? I have
   a hard cap on iterations but that's crude. (Also Day 19.)
3. How do I evaluate whether the agent's reasoning was good, separate from
   whether the final answer was correct? (Day 15 problem.)
4. How do I structure tool definitions so the LLM uses them correctly more
   often? (Day 4 and Day 23 problem.)

## What I'm building toward

Tomorrow (Day 3): native tool use, structured tool definitions, multiple tools.
The agent gets a calculator, file reader, maybe one more tool. Tool design is
where most agent failures actually live, and we'll feel that tomorrow.

By end of Week 1: this hand-rolled loop gets retired and replaced with
LangGraph. The point of building it by hand was to know what the framework is
abstracting. From now on when I see LangGraph state machines, I'll know
exactly what they're doing under the hood.

## LinkedIn post draft (for Day 7, maybe earlier)

Theme: "Every agent framework is a wrapper around six lines of code. Here are
the six lines."

Hook: Built a ReAct loop from scratch today before touching LangGraph. I now
understand frameworks better than people who only know frameworks.