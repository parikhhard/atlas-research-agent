"""
Atlas — multi-agent orchestrator-worker version.

Day 8: A planner decomposes the user query into sub-tasks. Workers handle
each sub-task. A synthesizer combines results into a coherent answer.

This is structured multi-agent. The orchestrator is explicit (planner +
synthesizer nodes), workers are stateless and specialized. Compare to the
single-agent versions in agent/react.py and agent/graph.py.
"""

import json
import os
import warnings
from typing import TypedDict, Annotated
from langgraph.types import Send

import httpx
from anthropic import Anthropic
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, ToolMessage
from operator import add

from tools import TOOL_DEFINITIONS, execute_tool

warnings.filterwarnings("ignore")
load_dotenv()


# Corporate cert bypass
anthropic_client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    http_client=httpx.Client(verify=False),
)

llm = ChatAnthropic(model="claude-sonnet-4-5", max_tokens=4096)
llm._client = anthropic_client
llm_with_tools = llm.bind_tools(TOOL_DEFINITIONS)


PLANNER_PROMPT = """You are a research planner.

Given a user query, decide whether it needs decomposition into sub-tasks.

If the query asks for one fact, return a single sub-task that is the
original query.

If the query involves comparisons, multi-part questions, or genuinely
independent pieces of information, break it into 2 to 4 sub-tasks.

Return ONLY a JSON array of strings. No preamble. No commentary.

Examples:

Query: "What is the population of Tokyo?"
Response: ["What is the current population of Tokyo?"]

Query: "Compare the populations of Tokyo, New York, and London"
Response: ["What is the current population of Tokyo?", "What is the current population of New York City?", "What is the current population of London?"]

Query: "What's the latest news about Anthropic and OpenAI this week?"
Response: ["What is the latest news about Anthropic this week?", "What is the latest news about OpenAI this week?"]
"""


WORKER_PROMPT = """You are a focused research worker.

You will be given a single specific research question. Use the available tools
to answer it. Be efficient. Do not loop more than necessary.

When you have enough information, respond with a concise factual answer in 2
to 3 sentences. Include sources if you used the search tool.
"""


SYNTHESIZER_PROMPT = """You are a research synthesizer.

You receive a list of sub-questions and the answers researched for each.
Your job is to combine them into a single coherent answer to the user's
original question.

Be specific. Quote concrete facts from the worker results. Do not invent
information that wasn't in the results. If results contradict each other,
surface the contradiction rather than hiding it.

Keep the final answer concise.
"""


class MultiAgentState(TypedDict):
    query: str
    sub_tasks: list
    completed_tasks: Annotated[list, add]  # parallel workers append here
    final_answer: str
    trace: Annotated[list, add]  # parallel workers add trace events here


def planner_node(state):
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=PLANNER_PROMPT,
        messages=[{"role": "user", "content": state["query"]}],
    )
    text = response.content[0].text.strip()
    
    # Strip markdown code fences if Claude wrapped the JSON
    if text.startswith("```"):
        # Remove opening fence (```json or just ```)
        text = text.split("\n", 1)[1] if "\n" in text else text
        # Remove closing fence
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()
    
    # Find the JSON array in the response (in case there's prose before it)
    if "[" in text and "]" in text:
        start = text.index("[")
        end = text.rindex("]") + 1
        text = text[start:end]
    
    try:
        sub_tasks = json.loads(text)
        if not isinstance(sub_tasks, list) or not all(isinstance(t, str) for t in sub_tasks):
            sub_tasks = [state["query"]]
    except json.JSONDecodeError:
        sub_tasks = [state["query"]]
    
    new_trace = state["trace"] + [{
        "step": "planning",
        "content": f"Decomposed into {len(sub_tasks)} sub-task(s): {sub_tasks}"
    }]
    
    return {"sub_tasks": sub_tasks, "trace": new_trace}

def run_worker(task: str) -> str:
    """Run a single worker on a single sub-task. Returns the answer string."""
    messages = [HumanMessage(content=task)]
    max_iterations = 5
    
    for _ in range(max_iterations):
        response = llm_with_tools.invoke([
            {"role": "system", "content": WORKER_PROMPT}
        ] + messages)
        
        tool_calls = getattr(response, "tool_calls", None) or []
        
        if not tool_calls:
            # Worker is done. Extract the final text.
            content = response.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text = ""
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text += block["text"]
                return text
            return str(content)
        
        # Execute tool calls and continue the loop
        messages.append(response)
        for call in tool_calls:
            result = execute_tool(call["name"], call["args"])
            messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
    
    return "Worker exceeded maximum iterations without producing an answer."


def worker_node(state):
    """
    Process a single sub-task. The Send API passes the specific task to this node.
    
    Notice: this node now receives a task directly via state["task"], not by
    looking at completed_tasks vs sub_tasks. Each parallel invocation is
    independent and stateless.
    """
    current_task = state["task"]
    answer = run_worker(current_task)
    
    return {
        "completed_tasks": [{"task": current_task, "answer": answer}],
        "trace": [{"step": "worker", "task": current_task, "answer": answer}],
    }


def synthesizer_node(state):
    """Combine all worker results into a final coherent answer."""
    summary = "\n\n".join([
        f"Sub-question {i+1}: {task['task']}\nAnswer: {task['answer']}"
        for i, task in enumerate(state["completed_tasks"])
    ])
    
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYNTHESIZER_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Original question: {state['query']}\n\nResearch results:\n{summary}"
        }],
    )
    
    final = response.content[0].text
    new_trace = state["trace"] + [{
        "step": "synthesis",
        "content": final
    }]
    
    return {"final_answer": final, "trace": new_trace}


def dispatch_workers(state):
    """
    Dispatch one parallel worker invocation per sub-task.
    
    Each Send creates a separate worker invocation with its own slice of state.
    LangGraph runs them all in parallel.
    """
    return [
        Send("worker", {"task": task})
        for task in state["sub_tasks"]
    ]

workflow = StateGraph(MultiAgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("worker", worker_node)
workflow.add_node("synthesizer", synthesizer_node)

workflow.set_entry_point("planner")

# Dispatch parallel workers after planning
workflow.add_conditional_edges("planner", dispatch_workers, ["worker"])

# All workers converge on the synthesizer
workflow.add_edge("worker", "synthesizer")
workflow.add_edge("synthesizer", END)

multi_graph = workflow.compile()


import time


def run_multi_agent(query: str) -> dict:
    """Public entry point. Runs planner -> parallel workers -> synthesizer."""
    initial_state = {
        "query": query,
        "sub_tasks": [],
        "completed_tasks": [],
        "final_answer": "",
        "trace": [],
    }
    
    start = time.time()
    final_state = multi_graph.invoke(initial_state)
    elapsed = time.time() - start
    
    return {
        "answer": final_state["final_answer"],
        "trace": final_state["trace"],
        "iterations": len(final_state["completed_tasks"]),
        "sub_tasks": final_state["sub_tasks"],
        "elapsed_seconds": round(elapsed, 2),
    }


if __name__ == "__main__":
    queries = [
        "What is the current population of Tokyo?",
        "Compare the populations of Tokyo, New York, and London. Which is largest?",
        "What's the latest news about Anthropic and OpenAI in 2026?",
    ]
    
    for q in queries:
        print(f"\n{'=' * 60}")
        print(f"QUERY: {q}")
        print(f"{'=' * 60}")
        result = run_multi_agent(q)
        print(f"\nSub-tasks ({len(result['sub_tasks'])}):")
        for st in result["sub_tasks"]:
            print(f"  - {st}")
        print(f"\nFINAL: {result['answer']}")