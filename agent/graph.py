"""
Atlas — LangGraph version with Postgres checkpointing.

Day 6: The graph now persists every state transition to Postgres.
Conversations survive restarts. Threads enable multi-session continuity.
"""

import os
import warnings
from typing import TypedDict, Annotated

import httpx
from anthropic import Anthropic
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from tools import TOOL_DEFINITIONS, execute_tool
from prompts import get_prompt

warnings.filterwarnings("ignore")
load_dotenv()


# Anthropic client with corporate cert bypass
anthropic_client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    http_client=httpx.Client(verify=False),
)

llm = ChatAnthropic(model="claude-sonnet-4-5", max_tokens=4096)
llm._client = anthropic_client
llm = llm.bind_tools(TOOL_DEFINITIONS)


# State definition unchanged from day 5
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    trace: list
    mode: str


def agent_node(state):
    system_prompt = get_prompt(state["mode"])
    response = llm.invoke([{"role": "system", "content": system_prompt}] + state["messages"])
    return {
        "messages": [response],
        "trace": state["trace"] + [{"step": "thought", "content": str(response.content)}],
    }


def tools_node(state):
    last = state["messages"][-1]
    results = []
    new_trace = list(state["trace"])
    for call in last.tool_calls:
        result = execute_tool(call["name"], call["args"])
        new_trace.append({"step": "action", "tool": call["name"], "input": call["args"]})
        new_trace.append({"step": "observation", "content": result})
        results.append(ToolMessage(content=result, tool_call_id=call["id"]))
    return {"messages": results, "trace": new_trace}


def should_continue(state):
    if state["messages"][-1].tool_calls:
        return "tools"
    return "end"


# Build the graph structure (same as day 5)
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tools_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
workflow.add_edge("tools", "agent")


# ---------- The new part: persistence ----------

# Create the checkpointer using the Postgres connection string
DATABASE_URL = os.environ["DATABASE_URL"]

# PostgresSaver.from_conn_string returns a context manager. We enter it once
# at module load and keep it open for the lifetime of the process. In a real
# production system you'd manage this lifecycle more carefully.
_checkpointer_ctx = PostgresSaver.from_conn_string(DATABASE_URL)
checkpointer = _checkpointer_ctx.__enter__()

# First-time setup: create the tables LangGraph needs in your Postgres database.
# This is idempotent, safe to call every startup.
checkpointer.setup()

# Compile the graph WITH the checkpointer attached
graph = workflow.compile(checkpointer=checkpointer)


# ---------- The new entry point: accepts a thread_id ----------

def run_agent_graph(user_query, mode="fast", thread_id="default"):
    """
    Run a query through the persistent graph.
    
    thread_id identifies the conversation. Same thread_id = same conversation,
    state restored from checkpoint. New thread_id = new conversation.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    final_state = graph.invoke(
        {
            "messages": [HumanMessage(content=user_query)],
            "trace": [],
            "mode": mode,
        },
        config=config,
    )
    
    answer = final_state["messages"][-1].content
    return {
        "answer": str(answer),
        "trace": final_state["trace"],
        "iterations": len(final_state["trace"]),
        "mode": mode,
        "thread_id": thread_id,
    }


def get_history(thread_id):
    """
    Retrieve the full state history of a thread.
    Useful for debugging and replay.
    """
    config = {"configurable": {"thread_id": thread_id}}
    history = []
    for snapshot in graph.get_state_history(config):
        history.append({
            "values": str(snapshot.values),
            "next": list(snapshot.next),
            "created_at": str(snapshot.created_at) if snapshot.created_at else None,
        })
    return history


if __name__ == "__main__":
    import uuid
    
    # First turn: new conversation
    thread = str(uuid.uuid4())
    print(f"\nThread: {thread}\n")
    
    result1 = run_agent_graph(
        "What is the weather in Austin today?",
        mode="fast",
        thread_id=thread,
    )
    print(f"Turn 1: {result1['answer']}\n")
    
    # Second turn: SAME thread. The agent should remember the first turn.
    result2 = run_agent_graph(
        "What is the weather in Austin tomorrow?",
        mode="fast",
        thread_id=thread,
    )
    print(f"Turn 2: {result2['answer']}\n")
    
    # Show the history
    print("State history for this thread:")
    for snapshot in get_history(thread):
        print(f"  {snapshot['created_at']} -> next: {snapshot['next']}")