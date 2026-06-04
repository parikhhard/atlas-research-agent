"""
Current time tool. Lets the agent know what 'now' is.

This matters because the LLM's training data has a cutoff and it doesn't
know the actual current date. Without this, the agent will confidently
state outdated information as current.
"""

from datetime import datetime


TIME_DEFINITION = {
    "name": "current_time",
    "description": (
        "Get the current date and time. "
        "Use this when the user asks anything about 'today', 'now', 'this week', "
        "or anything time relative. Your training data has a cutoff, so you do "
        "not actually know what today's date is without calling this tool."
    ),
    "input_schema": {
        "type": "object",
        "properties": {}
    }
}


def current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z (current time)")


if __name__ == "__main__":
    print(current_time())