# Day 3 — Tool Design

## Core insight of the day

Tool design is harder than prompting. The LLM reads the tool description to
decide whether and how to use the tool. The description is doing prompt
engineering for one specific decision, and it has to do it under uncertainty,
across thousands of possible user queries, without context I can give it
upfront.

Three concrete things I observed today:

1. The agent over-uses tools when descriptions are vague. "Searches the web"
   gets called for everything. "Search the web for current information you
   don't already know, do not use for math or established facts" gets called
   correctly.

2. The agent under-uses tools when descriptions are too narrow. Early
   calculator description said "for math." Agent did mental math even for
   ratios. Description rewrite to "use for multi-digit arithmetic,
   percentages, ratios" fixed it.

3. The single biggest unlock today was the "do not use for X" clause. The
   negative space in a description shapes behavior more than the positive
   space. Worth memorizing.

## The registry pattern paid off immediately

By the third tool I was glad I refactored early. Adding `current_time` took
about 8 minutes total because the pattern was: write the function, write the
definition, register both. No changes to the agent loop. No changes to the
API. The agent automatically knew about the new tool.

This is a generalizable lesson: when you're going to add many of something,
build the registry first. Don't write the third one and then refactor. Write
the second one and refactor immediately.

## Multi-tool chains

The population ratio query was the first time Atlas did something I would
call "real" research behavior. Two parallel searches, then a calculation on
the result. Three iterations total. Watching the trace, I could see the
agent's internal logic: "I need both populations to compute the ratio. I'll
search for both. Now I have them. Now I'll calculate."

That sequence is the simplest example of what makes agents valuable. No
human wrote the control flow. The LLM derived it from the goal and the
available tools. Even though the example is trivial, the pattern scales to
genuinely complex research where the path isn't known upfront.

## Failure modes I noticed

**Over-tooling.** Agent called search for facts it definitely knew. Fixed
by sharpening the search description.

**Wasted iterations.** Agent occasionally called search, then searched the
same thing slightly differently. Need a way to detect duplicate calls. (Day
19 problem.)

**Trusting tool output blindly.** When search returned conflicting info,
agent picked the first result. No source weighting. (Day 17 problem with
critic agents.)

**The calculator could be tricked.** Even with AST parsing, the LLM passes
weird expressions. I logged a couple cases where it tried things like
"1.7 million" instead of "1700000". Need better input normalization or a
clearer description. (Could fix today, deferring.)

## What I'm building toward

Tomorrow (Day 4): system prompts as the deepest lever for shaping agent
behavior. Today I shaped behavior through tool descriptions. Tomorrow I'll
do it through the system prompt, and learn which lever to pull for which
problem.

By end of Week 1: this hand-rolled agent gets replaced with LangGraph. The
tools and descriptions carry over. The loop logic gets retired.

## LinkedIn post draft

Theme: "Tool descriptions are doing prompt engineering for the model's
tool-selection decision. Most agent failures are tool design failures, not
model failures."