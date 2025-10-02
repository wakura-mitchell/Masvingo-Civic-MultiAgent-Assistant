"""
Handles query logic and retrieval from the vector database.
"""


from typing import List, Dict, Any

class VectorDBQuery:
    """
    Handles query logic and retrieval from the vector database.
    """
    def __init__(self, connection, embedding_model):
        self.connection = connection
        self.embedding_model = embedding_model
        self.collection = self.connection.get_collection()

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector database, chunking and embedding them.
        Args:
            documents: List of documents, each a dict with 'content' and 'metadata'
        """
        all_chunks = []
        all_ids = []
        all_metadatas = []

        for doc_idx, doc in enumerate(documents):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            title = metadata.get("title", f"doc_{doc_idx}")

            # Chunk the document content
            chunks = self.chunk_text(content, title)

            # Collect chunk data
            for chunk in chunks:
                all_chunks.append(chunk["content"])
                all_ids.append(chunk["chunk_id"])
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "title": chunk["title"],
                    "chunk_id": chunk["chunk_id"],
                })
                all_metadatas.append(chunk_metadata)

        # Create embeddings for all chunks
        all_embeddings = self.embedding_model.embed(all_chunks)

        # Add to ChromaDB collection
        self.collection.add(
            ids=all_ids,
            documents=all_chunks,
            metadatas=all_metadatas,
            embeddings=all_embeddings.tolist() if hasattr(all_embeddings, "tolist") else all_embeddings,
        )

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
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=200,
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

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search for similar documents in the vector database.
        Args:
            query: Search query
            n_results: Number of results to return
        Returns:
            Dictionary containing search results with keys: 'documents', 'metadatas', 'distances', 'ids'
        """
        query_embedding = self.embedding_model.embed([query])
        results = self.collection.query(
            query_embeddings=query_embedding.tolist() if hasattr(query_embedding, "tolist") else query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        if not results or not results.get("documents"):
            return {
                "documents": [],
                "metadatas": [],
                "distances": [],
                "ids": [],
            }
        return results
