"""
URL fetch tool with retry.
"""

import httpx
import re

from tools.reliability import with_retry


FETCH_DEFINITION = {
    "name": "fetch_url",
    "description": (
        "Fetch the text content of a web page at a given URL. "
        "Use this when you need to read the full content of a page, "
        "typically after a search returned a URL that looks promising. "
        "Returns the text content with HTML stripped, truncated to 5000 characters."
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


@with_retry(max_attempts=3, base_delay=1.0)
def fetch_url(url: str) -> str:
    with httpx.Client(verify=False, follow_redirects=True, timeout=10.0) as client:
        response = client.get(url, headers={"User-Agent": "Atlas-Research-Agent/0.1"})
        response.raise_for_status()
    
    text = response.text
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) > 5000:
        text = text[:5000] + "\n\n[Content truncated at 5000 characters]"
    
    return text