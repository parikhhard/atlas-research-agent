# Day 6 — Persistent Agent State

## Core insight

State machine plus checkpointer is the architecture every production agent
converges on. Today proved it. The graph I compiled yesterday became a
persistent agent today by adding one wrapper. The state schema, the nodes,
the edges, none of them changed. Persistence is decoration on top.

## What this unlocks

Three things, each of them non-negotiable for production:

1. Long running tasks survive restarts. The server crashes, the user comes
   back, the conversation resumes from the last checkpoint.

2. Multi session conversations work. A user starts a research task on
   Monday, follows up Wednesday. Same thread_id, full context preserved.

3. Auditability. Every state transition is in Postgres. When an agent does
   something wrong, I can replay every step to find out where it went off
   the rails.

## The thread_id is the unit of conversation

This took me a minute to internalize. The thread_id is the only thing that
distinguishes one conversation from another. Two different users get two
different threads. The same user starting fresh gets a new thread. Every
invocation against a thread_id reads the latest checkpoint for that thread
and runs from there.

That's it. There is no "session" object, no "user" object, no special
conversation model. Just a string that ties checkpoints together.

In production I'd derive thread_id from a combination of user_id and
conversation_id from my application database. The agent itself stays
oblivious to who the user is. It only knows the thread.

## Cost and tradeoffs

Checkpointing every state transition isn't free.

- Latency: writing to Postgres adds a few milliseconds per node. Not
  noticeable for research tasks at 5-30 second loops. Would matter for
  high QPS use cases.
- Storage: every checkpoint stores the full state. Long conversations get
  expensive. In production I'd need a retention policy: maybe keep full
  history for 30 days, then summarize and drop intermediate steps.
- Schema migrations: when I change the State TypedDict, old checkpoints
  with the old schema are now invalid. Need a migration story. Defer.

## Where this connects to FLIK

FLIK does not have agent state. Every query is stateless. That's correct
for FLIK because the system is a workflow, not an agent. There is no
conversation to persist.

If I were to build a follow-up version of FLIK with multi-turn capability
(the user asks a question, then asks a follow-up that references the prior
answer), this is exactly the architecture I'd reach for. Same pattern,
different problem.

## The interview answer

"How do you handle agent state in production?"

State machine plus checkpointer. The agent is a LangGraph state graph. State
is a TypedDict that flows through every node. I attach a Postgres
checkpointer at compile time, so every state transition persists. The
thread_id ties checkpoints together into a conversation. Restarts don't
lose state. Multi-session continuity works for free. Every transition is
audit-able by querying the checkpoints table.

That's the answer. It's specific, it's correct, and most candidates can't
give it. After today, you can.

## What I'm holding for later

1. State schema evolution. When I add fields to AgentState next week, what
   happens to old checkpoints? Need a migration story. (Probably Week 3.)
2. Memory beyond messages. Right now state holds messages, trace, mode.
   For richer agents I'll need long-term memory, vector embeddings, etc.
   (Day 11.)
3. Multi-user thread isolation. Right now anyone can pass any thread_id
   and access any conversation. Need auth-based thread scoping. (Week 2.)
4. Checkpoint cleanup. Old conversations accumulate. Need retention.
   (Week 3.)

## LinkedIn post angle

"Most AI agent demos lose all state when you close the tab. Production
agents have to persist across restarts, across sessions, across days. The
moment to stop calling something an agent and start calling it a system is
when state survives the server. Took me one extra wrapper around my
LangGraph compile call to get there. The framework's value isn't in the
code I wrote today. It's in the code I didn't have to rewrite."