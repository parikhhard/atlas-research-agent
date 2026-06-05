# Day 4 — System Prompts as Architecture

## Core insight

The system prompt is the architecture, not decoration. Six implicit sections
deserve to be explicit: identity, capabilities, behavior rules, constraints,
output format, stopping conditions. Most prompts I've seen in production
collapse these into a paragraph and the agent reads them inconsistently. A
prompt with the sections separated is reliably followed.

## What surprised me

The same model, same tools, same query produced visibly different behavior
when only the prompt changed. The fast mode answered "what is 47 times 89"
directly without calling the calculator. The thorough mode called it. The
fast mode used one search and returned three sentences. The thorough mode
used two and returned the structured ANSWER/REASONING/SOURCES/CONFIDENCE
block I asked for.

That's the same model. The behavior delta is entirely in the prompt.

This is the lever most engineers underestimate. Tool descriptions control
which tool gets used. The system prompt controls how the agent reasons,
stops, formats, and trades off uncertainty against speed. They are different
levers for different problems.

## The diagnostic question

When an agent misbehaves, ask: is this a prompt problem or a tool problem?

- If the agent uses the wrong tool: tool description.
- If the agent uses no tools when it should: prompt or tool description.
- If the agent uses too many tools: prompt (stopping conditions).
- If the output format is wrong: prompt (output format section).
- If the agent loops: prompt (stopping conditions) or tool design (idempotency).
- If the agent says things you wish it wouldn't: prompt (constraints).

This single diagnostic skill, applied consistently, would fix most of the
"my agent is broken" posts I see online.

## Where I'd push this further

The thorough mode prompt asks for a CONFIDENCE field. That's a structured
self assessment. Right now it's vibes based. A more rigorous version would
ground confidence in actual signal: number of sources, source recency,
whether sources agreed. That's a critic agent pattern (Day 17 work).

I also notice that the thorough mode is more honest about uncertainty than
the fast mode. Fast mode tends to assert; thorough mode tends to qualify.
That's a feature for some users and a bug for others. Mode selection ends
up being a tradeoff between confidence theater and intellectual honesty,
and the right answer depends on the use case.

## Where this connects to FLIK

The closest analog at work is intent classification. We route different
question types to different paths. The mode switching today is the same
idea, applied at the prompt layer instead of the routing layer. In FLIK,
numeric questions went to SQL generation; conversational questions went to
RAG. Same retrieval, same database, different processing paths.

In Atlas, fast and thorough are different processing paths for the same
underlying agent. Same model, same tools, different prompts.

The pattern: when you have one engine that needs to behave differently for
different classes of input, push the differentiation as close to the prompt
as possible and reuse everything else. Cheaper than building two engines.

## LinkedIn post draft

Theme: "The system prompt is the architecture. Six sections every production
agent prompt should have. Most prompts I see in the wild have one paragraph
that smushes all six together and then teams wonder why their agent is
inconsistent."