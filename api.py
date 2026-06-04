"""
Atlas API — FastAPI entry point.
"""

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
    result = run_agent(request["query"], verbose=False)
    return {
        "answer": result["answer"],
        "trace": result["trace"],
        "iterations": result["iterations"],
    }