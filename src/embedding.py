"""
Manages embedding model loading and vectorization.
"""


import os
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    """
    Manages embedding model loading and vectorization.
    """
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)

    def embed(self, texts):
        """
        Return vector embeddings for the given text(s).
        Args:
            texts: str or List[str]
        Returns:
            Embeddings as numpy array or list
        """
        return self.model.encode(texts, show_progress_bar=True)
