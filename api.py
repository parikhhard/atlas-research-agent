"""
Atlas API — FastAPI entry point.

Right now it's a thin wrapper around ask_claude. By end of Week 1 this will
stream multi-agent execution traces in real time. By Week 2 it will handle
persistent multi-session research tasks. By Week 3 it will be fully observable.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.core import ask_claude

app = FastAPI(title="Atlas Research Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {"status": "ok", "service": "atlas", "version": "0.1.0"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    answer = ask_claude(request.query)
    return QueryResponse(answer=answer)