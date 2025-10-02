
# Modular imports
from connection import VectorDBConnection
from embedding import EmbeddingModel
from query import VectorDBQuery

class VectorDB:
    """
    High-level orchestrator for vector database operations using modular components.
    """
    def __init__(self, collection_name: str = None, embedding_model: str = None, db_path: str = None):
        self.connection = VectorDBConnection(db_path=db_path, collection_name=collection_name)
        self.embedding_model = EmbeddingModel(model_name=embedding_model)
        self.query_engine = VectorDBQuery(self.connection, self.embedding_model)

    def add_documents(self, documents):
        """Add documents to the vector database."""
        self.query_engine.add_documents(documents)

    def search(self, query, n_results=5):
        """Search for similar documents in the vector database."""
        return self.query_engine.search(query, n_results=n_results)
