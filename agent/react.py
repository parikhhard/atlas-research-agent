"""
Atlas — ReAct loop with multi-tool support.

Day 3: Restructured to use the tool registry. Same loop, more tools.
The agent now has: search, calculate, fetch_url, current_time.
"""

import os
import warnings
import httpx
from anthropic import Anthropic
from dotenv import load_dotenv
from prompts import get_prompt

from tools import TOOL_DEFINITIONS, execute_tool

warnings.filterwarnings("ignore")
load_dotenv()

# Corporate cert bypass
http_client = httpx.Client(verify=False)

client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    http_client=http_client,
)

MAX_ITERATIONS = 10

SYSTEM_PROMPT = """You are Atlas, a research assistant with access to tools.

Available tools: search, calculate, fetch_url, current_time.

Use them when needed. Do not call tools you do not need. Do not call the same
tool with the same arguments twice. When you have enough information to answer
the user's question, respond directly with the final answer.

Be efficient. Tool calls cost time and money.
"""


def run_agent(user_query: str, mode: str = "fast", verbose: bool = True) -> dict:
    """
    Run the ReAct loop until the agent produces a final answer or hits max iterations.
    
    mode: 'fast' or 'thorough'. Controls the system prompt.
    """
    system_prompt = get_prompt(mode)
    messages = [{"role": "user", "content": user_query}]
    trace = []
    
    for iteration in range(MAX_ITERATIONS):
        if verbose:
            print(f"\n--- Iteration {iteration + 1} ---")
        
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )
        
        if response.stop_reason == "end_turn":
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
                "mode": mode,
            }
        
        if response.stop_reason == "tool_use":
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
                    
                    result = execute_tool(tool_name, tool_input)
                    
                    if verbose:
                        result_preview = result[:200] if len(result) > 200 else result
                        print(f"OBSERVATION: {result_preview}...")
                    trace.append({
                        "step": "observation",
                        "content": result
                    })
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result,
                    })
            
            messages.append({"role": "user", "content": tool_results})
            continue
        
        return {
            "answer": f"Unexpected stop reason: {response.stop_reason}",
            "trace": trace,
            "iterations": iteration + 1,
        }
    
    return {
        "answer": "Agent exceeded maximum iterations without producing a final answer.",
        "trace": trace,
        "iterations": MAX_ITERATIONS,
    }


if __name__ == "__main__":
    test_queries = [
        "What's 47 times 89?",
        "What time is it right now?",
        "What's the current population of Tokyo divided by the current population of New York City?",
        "Find the latest article on Anthropic's blog and tell me what it's about.",
    ]
    
    for q in test_queries:
        print(f"\n{'=' * 60}")
        print(f"QUERY: {q}")
        print(f"{'=' * 60}")
        result = run_agent(q)
        print(f"\nFINAL: {result['answer']}")
        print(f"Iterations: {result['iterations']}")