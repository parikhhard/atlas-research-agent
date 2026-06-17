"""Stress test the compaction layer with a multi-turn conversation."""

import uuid
import requests

API = "http://localhost:8000"
thread = str(uuid.uuid4())

queries = [
    "What is the current population of Tokyo?",
    "What about New York City?",
    "What about London?",
    "Which of those three is largest?",
    "How does Tokyo's population compare to its land area?",
    "What's the population density of Tokyo?",
    "Is Tokyo's population growing or shrinking?",
    "What are the main drivers of that trend?",
    "Compare that trend to Seoul.",
    "Now summarize everything we've discussed.",
]

for i, q in enumerate(queries):
    print(f"\n--- Turn {i+1}: {q[:60]}...")
    r = requests.post(
        f"{API}/query",
        json={"query": q, "thread_id": thread, "engine": "graph"},
    )
    data = r.json()
    
    state = requests.get(f"{API}/state/{thread}").json()
    print(f"Answer: {data['answer'][:150]}...")
    print(f"State: {state['message_count']} messages, ~{state['estimated_tokens']} tokens")