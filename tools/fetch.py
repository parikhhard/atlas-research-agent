"""
URL fetch tool. Lets the agent read a specific web page.

Use case: search returns a URL, agent wants to read the full content.
"""

import httpx


FETCH_DEFINITION = {
    "name": "fetch_url",
    "description": (
        "Fetch the text content of a web page at a given URL. "
        "Use this when you need to read the full content of a page, "
        "typically after a search returned a URL that looks promising. "
        "Returns the text content with HTML stripped, truncated to 5000 characters. "
        "Do not use to search the web — use the search tool for that."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The full URL to fetch, including https://"
            }
        },
        "required": ["url"]
    }
}


def fetch_url(url: str) -> str:
    """Fetch a URL and return text content, truncated."""
    try:
        with httpx.Client(verify=False, follow_redirects=True, timeout=10.0) as client:
            response = client.get(url, headers={"User-Agent": "Atlas-Research-Agent/0.1"})
            response.raise_for_status()
        
        # Cheap HTML stripping — good enough for now
        text = response.text
        # Remove script and style blocks first
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate
        if len(text) > 5000:
            text = text[:5000] + "\n\n[Content truncated at 5000 characters]"
        
        return text
    except Exception as e:
        return f"Error fetching URL: {type(e).__name__}: {str(e)}"


if __name__ == "__main__":
    print(fetch_url("https://www.anthropic.com/research/building-effective-agents")[:1000])