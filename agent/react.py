"""
A ReAct loop, hand-built. No framework.

The agent receives a query, decides whether to use a tool or answer directly,
executes the tool if needed, observes the result, and decides again. Loops
until it has a final answer or hits a max iteration cap.

This is intentionally written without any agent framework. The point is to
feel the bare metal of how agents work before reaching for LangGraph on Day 5.
"""

import json
import os
import warnings
import httpx
from anthropic import Anthropic
from dotenv import load_dotenv

from tools.search import search

warnings.filterwarnings("ignore")
load_dotenv()

# Corporate cert bypass
http_client = httpx.Client(verify=False)

client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    http_client=http_client,
)

MAX_ITERATIONS = 10

SYSTEM_PROMPT = """You are Atlas, a research assistant.

You have access to one tool:
- search(query: str): searches the web and returns results

Your job: answer the user's question. If you need fresh information, use the
search tool. If the question is conceptual and you already know the answer,
respond directly.

When you have enough information, give a final answer to the user.

Be efficient. Don't search if you don't need to. Don't search the same thing
twice. Don't exceed three searches per question unless absolutely necessary.
"""

# Tool definition in Anthropic's tool-use format
TOOLS = [
    {
        "name": "search",
        "description": "Search the web for current information. Use this when you need facts you don't already know, especially anything time-sensitive.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific and concise."
                }
            },
            "required": ["query"]
        }
    }
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Dispatch to the right tool. Right now we only have one."""
    if tool_name == "search":
        return search(tool_input["query"])
    return f"Unknown tool: {tool_name}"


def run_agent(user_query: str, verbose: bool = True) -> dict:
    """
    Run the ReAct loop until the agent produces a final answer or hits max iterations.
    
    Returns a dict with:
        - answer: final text response
        - trace: list of every step the agent took (for debugging and display)
        - iterations: how many loops it took
    """
    messages = [{"role": "user", "content": user_query}]
    trace = []
    
    for iteration in range(MAX_ITERATIONS):
        if verbose:
            print(f"\n--- Iteration {iteration + 1} ---")
        
        # Step 1: Ask Claude what to do next
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        
        # Step 2: Check what Claude decided
        if response.stop_reason == "end_turn":
            # Claude is done. Extract the final text answer.
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            
            trace.append({"step": "final_answer", "content": final_text})
            if verbose:
                print(f"FINAL ANSWER: {final_text}")
            
            return {
                "answer": final_text,
                "trace": trace,
                "iterations": iteration + 1,
            }
        
        if response.stop_reason == "tool_use":
            # Claude wants to call a tool. Find which one(s).
            assistant_message = {"role": "assistant", "content": response.content}
            messages.append(assistant_message)
            
            tool_results = []
            for block in response.content:
                if block.type == "text":
                    if verbose:
                        print(f"THOUGHT: {block.text}")
                    trace.append({"step": "thought", "content": block.text})
                
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id
                    
                    if verbose:
                        print(f"ACTION: {tool_name}({tool_input})")
                    trace.append({
                        "step": "action",
                        "tool": tool_name,
                        "input": tool_input
                    })
                    
                    # Execute the tool
                    result = execute_tool(tool_name, tool_input)
                    
                    if verbose:
                        print(f"OBSERVATION: {result[:200]}...")
                    trace.append({
                        "step": "observation",
                        "content": result
                    })
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result,
                    })
            
            # Send tool results back to Claude for the next iteration
            messages.append({"role": "user", "content": tool_results})
            continue
        
        # Unexpected stop reason
        return {
            "answer": f"Unexpected stop reason: {response.stop_reason}",
            "trace": trace,
            "iterations": iteration + 1,
        }
    
    # Hit max iterations without finishing
    return {
        "answer": "Agent exceeded maximum iterations without producing a final answer.",
        "trace": trace,
        "iterations": MAX_ITERATIONS,
    }


if __name__ == "__main__":
    result = run_agent("What is the current population of Tokyo? Cite your source.")
    print("\n" + "=" * 60)
    print(f"Agent completed in {result['iterations']} iterations.")
    print(f"Final answer: {result['answer']}")