"""
Tool registry. Every tool registers itself here.

The agent reads TOOL_DEFINITIONS (for the LLM) and TOOL_FUNCTIONS (for execution).
Adding a new tool: import the module, then add the entries.
"""

from tools.search import search, SEARCH_DEFINITION
from tools.calculator import calculate, CALCULATOR_DEFINITION
from tools.fetch import fetch_url, FETCH_DEFINITION
from tools.time_now import current_time, TIME_DEFINITION


# Tool definitions for the LLM
TOOL_DEFINITIONS = [
    SEARCH_DEFINITION,
    CALCULATOR_DEFINITION,
    FETCH_DEFINITION,
    TIME_DEFINITION,
]

# Tool name -> function mapping for execution
TOOL_FUNCTIONS = {
    "search": search,
    "calculate": calculate,
    "fetch_url": fetch_url,
    "current_time": current_time,
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Dispatch a tool call to the right function."""
    if tool_name not in TOOL_FUNCTIONS:
        return f"Error: unknown tool '{tool_name}'"
    
    try:
        return TOOL_FUNCTIONS[tool_name](**tool_input)
    except Exception as e:
        return f"Tool error: {type(e).__name__}: {str(e)}"