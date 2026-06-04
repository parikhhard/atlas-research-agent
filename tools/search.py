"""
Web search tool. Wraps Tavily.
"""

import os
import urllib3
from tavily import TavilyClient
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
tavily.session.verify = False


SEARCH_DEFINITION = {
    "name": "search",
    "description": (
        "Search the web for current information. "
        "Use this when you need facts you don't already know, "
        "especially anything time sensitive like current events, recent prices, "
        "today's news, weather, or live data. "
        "Do not use for math, well established facts, or things in your training data."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query. Be specific and concise. Include important keywords like dates or locations."
            }
        },
        "required": ["query"]
    }
}


def search(query: str, max_results: int = 3) -> str:
    response = tavily.search(query=query, max_results=max_results)
    results = []
    for r in response.get("results", []):
        results.append(f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n")
    return "\n---\n".join(results) if results else "No results found."