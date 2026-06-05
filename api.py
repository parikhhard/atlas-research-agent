"""
Atlas API.
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.react import run_agent

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
    result = run_agent(request["query"], mode=mode, verbose=False)
    return {
        "answer": result["answer"],
        "trace": result["trace"],
        "iterations": result["iterations"],
        "mode": result["mode"],
    }


@app.post("/compare")
async def compare(request: dict):
    """
    Run the same query through both modes and return side by side results.
    Useful for seeing how the system prompt alone changes agent behavior.
    """
    user_query = request["query"]
    
    # Run both modes in parallel using asyncio.to_thread since run_agent is sync
    fast_task = asyncio.to_thread(run_agent, user_query, "fast", False)
    thorough_task = asyncio.to_thread(run_agent, user_query, "thorough", False)
    
    fast_result, thorough_result = await asyncio.gather(fast_task, thorough_task)
    
    return {
        "fast": fast_result,
        "thorough": thorough_result,
    }