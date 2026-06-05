"""
System prompt registry. Each mode is a structured artifact, not a string literal.
Importing from here gives the agent loop a clean interface to switch modes.
"""

from prompts.fast import FAST_PROMPT
from prompts.thorough import THOROUGH_PROMPT


PROMPTS = {
    "fast": FAST_PROMPT,
    "thorough": THOROUGH_PROMPT,
}


def get_prompt(mode: str) -> str:
    """Return the system prompt for the requested mode, defaulting to fast."""
    return PROMPTS.get(mode, FAST_PROMPT)