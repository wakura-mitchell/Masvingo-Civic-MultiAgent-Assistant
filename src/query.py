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

    def search(self, query: str, n_results: int = 5, domain_filter: str = None) -> Dict[str, Any]:
        """
        Search for similar documents in the vector database.
        Args:
            query: Search query
            n_results: Number of results to return
            domain_filter: Optional domain to filter results by
        Returns:
            Dictionary containing search results with keys: 'documents', 'metadatas', 'distances', 'ids'
        """
        query_embedding = self.embedding_model.embed([query])
        results = self.collection.query(
            query_embeddings=query_embedding.tolist() if hasattr(query_embedding, "tolist") else query_embedding,
            n_results=n_results * 2,  # Get more results for filtering
            include=["documents", "metadatas", "distances"],
        )

        if not results or not results.get("documents"):
            return {
                "documents": [],
                "metadatas": [],
                "distances": [],
                "ids": [],
            }

        # Apply domain filtering if specified
        if domain_filter:
            filtered_results = self._filter_by_domain(results, domain_filter, n_results)
            return filtered_results

        # Return top n_results if no filtering
        return {
            "documents": [results["documents"][0][:n_results]],
            "metadatas": [results["metadatas"][0][:n_results]],
            "distances": [results["distances"][0][:n_results]],
            "ids": [results["ids"][0][:n_results]] if "ids" in results else [[]],
        }

    def _filter_by_domain(self, results: Dict[str, Any], domain_filter: str, n_results: int) -> Dict[str, Any]:
        """
        Filter search results by domain.
        """
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0] if "ids" in results else []

        # Filter results by domain
        filtered_docs = []
        filtered_metadatas = []
        filtered_distances = []
        filtered_ids = []

        for doc, meta, dist, chunk_id in zip(documents, metadatas, distances, ids):
            chunk_domain = meta.get("domain", "unknown")
            if chunk_domain == domain_filter or domain_filter == "general":
                filtered_docs.append(doc)
                filtered_metadatas.append(meta)
                filtered_distances.append(dist)
                filtered_ids.append(chunk_id)

                if len(filtered_docs) >= n_results:
                    break

        # If no domain-specific results, fall back to general results
        if not filtered_docs:
            print(f"No results found for domain '{domain_filter}', falling back to general search")
            return {
                "documents": [documents[:n_results]],
                "metadatas": [metadatas[:n_results]],
                "distances": [distances[:n_results]],
                "ids": [ids[:n_results]] if ids else [[]],
            }

        return {
            "documents": [filtered_docs],
            "metadatas": [filtered_metadatas],
            "distances": [filtered_distances],
            "ids": [filtered_ids],
        }
