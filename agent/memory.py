"""
Short-term memory management for the Atlas agent.

Two responsibilities:
1. Estimate the token cost of the current conversation.
2. Compact the conversation when it exceeds a threshold by summarizing
   older messages and replacing them with a single summary.
"""

from anthropic import Anthropic


def estimate_tokens(messages) -> int:
    """
    Rough token count. tokens ~= characters / 4.
    
    Good enough for thresholding decisions. For precise counts use
    Anthropic's count_tokens endpoint or tiktoken.
    """
    total_chars = 0
    for msg in messages:
        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text", "")
                    total_chars += len(text)
    return total_chars // 4


SUMMARIZATION_PROMPT = """You are summarizing the earlier portion of a research conversation.

Your job: produce a concise summary that preserves the key facts, questions
asked, sources cited, and any unresolved threads.

Be specific. Quote concrete numbers and proper nouns. Do not invent details.
Do not include conversational filler.

Format the output as a single paragraph, 4 to 8 sentences max. Start with
"Earlier in this conversation, the user asked..." or similar.

Output ONLY the summary text. No preamble. No commentary.
"""


def summarize_messages(client: Anthropic, messages) -> str:
    """
    Compress a list of messages into a single summary string.
    """
    # Format messages into a readable transcript for the summarizer
    transcript_parts = []
    for msg in messages:
        role = "User" if msg.type == "human" else "Assistant" if msg.type == "ai" else "Tool"
        content = msg.content
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = " ".join(text_parts)
        transcript_parts.append(f"{role}: {content}")
    
    transcript = "\n\n".join(transcript_parts)
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=SUMMARIZATION_PROMPT,
        messages=[{"role": "user", "content": transcript}],
    )
    
    return response.content[0].text