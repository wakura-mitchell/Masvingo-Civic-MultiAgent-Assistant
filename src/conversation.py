"""
Conversation history utilities for multi-turn RAG assistant.
"""
from typing import List, Dict

def format_history(history: List[Dict[str, str]]) -> str:
    """
    Format conversation history for prompt input.
    Args:
        history: List of dicts with 'user' and 'assistant' keys
    Returns:
        String representation of the conversation
    """
    lines = []
    for turn in history:
        user = turn.get('user', '')
        assistant = turn.get('assistant', '')
        lines.append(f"User: {user}")
        lines.append(f"Assistant: {assistant}")
    return '\n'.join(lines)
