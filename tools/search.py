"""
Web search tool. Wraps Tavily so the agent has a single function it can call.
"""

import os
import urllib3
from tavily import TavilyClient
from dotenv import load_dotenv

# Suppress the "insecure request" warnings since we know we're bypassing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Force the Tavily SDK's internal requests.Session to skip cert verification
tavily.session.verify = False


def search(query: str, max_results: int = 3) -> str:
    """
    Search the web and return a concise string of results.
    
    Returns: A formatted string the LLM can read.
    """
    response = tavily.search(query=query, max_results=max_results)
    
    results = []
    for r in response.get("results", []):
        results.append(f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n")
    
    return "\n---\n".join(results) if results else "No results found."


if __name__ == "__main__":
    print(search("current population of Tokyo 2025"))