"""
agent/llm/utils.py — LLM Utilities
"""

from typing import List, Dict, Any


def estimate_tokens(text: str) -> int:
    """
    Roughly estimate the number of tokens in a string.
    Rule of thumb: 1 token ≈ 4 characters for English.
    """
    if not text:
        return 0
    return len(text) // 4


def count_messages_tokens(messages: List[Dict[str, Any]]) -> int:
    """
    Estimates total tokens in a list of OpenAI-style messages.
    """
    total = 0
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, str):
            total += estimate_tokens(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and "text" in part:
                    total += estimate_tokens(part["text"])
        total += 10
    return total


def truncate_by_tokens(content: str, max_tokens: int) -> str:
    """Truncates content to fit within token budget."""
    max_chars = max_tokens * 4
    if estimate_tokens(content) <= max_tokens:
        return content
    return content[:max_chars] + f"\n\n[TRUNCATED to {max_tokens} tokens]"


def truncate_content(content: str, max_chars: int = 5000) -> str:
    """Truncates a string to a maximum number of characters."""
    if len(content) <= max_chars:
        return content
    half = max_chars // 2
    return content[:half] + f"\n\n[... TRUNCATED ...]\n\n" + content[-half:]
