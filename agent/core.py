"""
Atlas — core agent module.

Day 1: The simplest possible primitive. Takes a query, returns Claude's response.
"""

import os
import httpx
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Corporate cert bypass: create an httpx client that skips SSL verification
http_client = httpx.Client(verify=False)

client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    http_client=http_client,
)


def ask_claude(query: str, system_prompt: str | None = None) -> str:
    """
    A primitive LLM call. No agent loop, no tools, no memory.
    """
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=system_prompt or "You are a helpful research assistant.",
        messages=[{"role": "user", "content": query}],
    )
    return response.content[0].text


if __name__ == "__main__":
    answer = ask_claude(
        "In two sentences, what's the difference between a workflow and an agent?"
    )
    print(answer)