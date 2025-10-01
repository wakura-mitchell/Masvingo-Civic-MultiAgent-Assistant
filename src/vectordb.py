import os
import chromadb
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import torch


class VectorDB:
    """
    A simple vector database wrapper using ChromaDB with HuggingFace embeddings.
    """

    def __init__(self, collection_name: str = None, embedding_model: str = None):
        """
        Initialize the vector database.

        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: HuggingFace model name for embeddings
        """
        self.collection_name = collection_name or os.getenv(
            "CHROMA_COLLECTION_NAME", "masvingo_city_council"
        )
        self.embedding_model_name = embedding_model or os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path="./databases/chroma_db")

        # Load embedding model
        print(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Masvingo City Council RAG document collection"},
        )

        print(f"Vector database initialized with collection: {self.collection_name}")

    def chunk_text(self, text: str, title: str, chunk_size: int = 500) -> List[Dict[str, Any]]:
        """
        Chunk text into smaller pieces with metadata.

        Args:
            text: Input text to chunk
            title: Title or identifier for the text
            chunk_size: Approximate number of characters per chunk

        Returns:
            List of dicts with keys: content, title, chunk_id
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,          # ~100 words per chunk
            chunk_overlap=200,              # Overlap to preserve context
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        raw_chunks = text_splitter.split_text(text)

        chunks = []
        for i, chunk in enumerate(raw_chunks):
            chunks.append({
                "content": chunk,
                "title": title,
                "chunk_id": f"{title}_{i}",
            })

        return chunks

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector database.

        Args:
            documents: List of documents, each a dict with 'content' and 'metadata'
        """
        print(f"Processing {len(documents)} documents...")
        all_chunks = []
        all_ids = []
        all_metadatas = []
        all_embeddings = []

        for doc_idx, doc in enumerate(documents):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            title = metadata.get("title", f"doc_{doc_idx}")

            # Chunk the document content
            chunks = self.chunk_text(content, title)
            print(f"Document {doc_idx} chunked into {len(chunks)} chunks.")

            # Collect chunk data
            for chunk in chunks:
                all_chunks.append(chunk["content"])
                all_ids.append(chunk["chunk_id"])
                # Combine metadata with chunk metadata
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "title": chunk["title"],
                    "chunk_id": chunk["chunk_id"],
                })
                all_metadatas.append(chunk_metadata)

        # Create embeddings for all chunks
        print("Creating embeddings for all chunks...")
        all_embeddings = self.embedding_model.encode(all_chunks, show_progress_bar=True)

        # Add to ChromaDB collection
        print(f"Adding {len(all_chunks)} chunks to the vector database collection...")
        self.collection.add(
            ids=all_ids,
            documents=all_chunks,
            metadatas=all_metadatas,
            embeddings=all_embeddings.tolist() if hasattr(all_embeddings, "tolist") else all_embeddings,
        )
        print("Documents added to vector database")

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search for similar documents in the vector database.

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            Dictionary containing search results with keys: 'documents', 'metadatas', 'distances', 'ids'
        """
        # Encode the query
        query_embedding = self.embedding_model.encode([query])

        # Query the collection
        results = self.collection.query(
            query_embeddings=query_embedding.tolist() if hasattr(query_embedding, "tolist") else query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        # Handle empty results
        if not results or not results.get("documents"):
            return {
                "documents": [],
                "metadatas": [],
                "distances": [],
                "ids": [],
            }

        return results
