"""
Atlas API — FastAPI entry point.

Day 6: Adds thread_id support for persistent multi-turn conversations
and a /history endpoint for inspecting state checkpoints.
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.react import run_agent
from agent.graph import run_agent_graph, get_history

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/query")
def query(request: dict):
    mode = request.get("mode", "fast")
    engine = request.get("engine", "graph")
    thread_id = request.get("thread_id", "default")
    
    if engine == "graph":
        result = run_agent_graph(request["query"], mode=mode, thread_id=thread_id)
    else:
        # Hand-rolled ReAct has no persistence
        result = run_agent(request["query"], mode=mode, verbose=False)
        result["thread_id"] = thread_id
    
    return result


@app.post("/compare")
async def compare(request: dict):
    """
    Run the same query through both engines and return side by side results.
    The graph engine uses a thread_id for persistence, the react engine doesn't.
    """
    user_query = request["query"]
    mode = request.get("mode", "fast")
    thread_id = request.get("thread_id", "compare-default")
    
    react_task = asyncio.to_thread(run_agent, user_query, mode, False)
    graph_task = asyncio.to_thread(run_agent_graph, user_query, mode, thread_id)
    
    react_result, graph_result = await asyncio.gather(react_task, graph_task)
    
    return {
        "react": react_result,
        "graph": graph_result,
    }


@app.get("/history/{thread_id}")
def history(thread_id: str):
    """Return the full state history for a given thread."""
    return {
        "thread_id": thread_id,
        "history": get_history(thread_id),
    }