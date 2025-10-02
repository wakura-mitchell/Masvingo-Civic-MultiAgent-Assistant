"""
Handles database connection and setup for vector database.
"""


import os
import chromadb

class VectorDBConnection:
    """
    Handles database connection and setup for vector database (ChromaDB).
    """
    def __init__(self, db_path: str = None, collection_name: str = None):
        self.db_path = db_path or "./databases/chroma_db"
        self.collection_name = collection_name or os.getenv("CHROMA_COLLECTION_NAME", "masvingo_city_council")
        self.client = None
        self.collection = None
        self._connect()

    def _connect(self):
        """Establish connection to the vector database and get/create collection."""
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Masvingo City Council RAG document collection"},
        )

    def get_collection(self):
        """Return the ChromaDB collection object."""
        return self.collection
