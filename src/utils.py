"""
Utility functions for vector database operations.
"""

import re

def clean_text(text: str) -> str:
    """Clean and preprocess text for embedding.
    Steps:
    - Lowercase
    - Remove special characters
    - Remove extra whitespace
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text)         # Remove extra whitespace
    return text.strip()
