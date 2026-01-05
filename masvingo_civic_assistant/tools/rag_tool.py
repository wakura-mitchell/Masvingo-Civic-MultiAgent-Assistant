"""
RAG Tool - Custom RAG retrieval tool using existing VectorDB with web scraping.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.logging_config import logger
import time
import yaml

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from tools.web_scraper_tool import WebScraperTool

# Load prompt configuration
project_root = Path(__file__).parent.parent
prompt_config_path = project_root / "config" / "prompt_config.yaml"

def load_prompt_config():
    """Load prompt configuration from YAML file."""
    try:
        with open(prompt_config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Failed to load prompt config: {e}")
        return {}

prompts = load_prompt_config()
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.logging_config import logger
import time
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

# Add src to path (if it exists)
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if src_path.exists():
    sys.path.append(str(src_path))

# Try to import existing RAG system, fallback to simple implementation
try:
    # Import from src.app explicitly
    import importlib.util
    spec = importlib.util.spec_from_file_location("src_app", str(src_path / "app.py"))
    src_app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(src_app)
    
    RAGAssistant = src_app.RAGAssistant
    load_documents = src_app.load_documents
    USE_EXISTING_RAG = True
except ImportError:
    USE_EXISTING_RAG = False
    logger.info("Using built-in RAG implementation")

from tools.web_scraper_tool import WebScraperTool

class SimpleRAGAssistant:
    """Simple RAG implementation for when the main one is not available."""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(project_root / "databases" / "chroma_db"))
        self.collection = self.client.get_or_create_collection("civic_docs")
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.documents = []
        logger.info("Simple RAG Assistant initialized")

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector database."""
        logger.info(f"Adding {len(documents)} documents to vector DB")
        valid_documents = []
        
        for doc in documents:
            content = doc.get("content", "").strip()
            metadata = doc.get("metadata", {})

            # Skip empty or very short content
            if not content or len(content) < 10:
                logger.warning(f"Skipping document with insufficient content: {len(content)} chars, metadata: {metadata}")
                continue
                
            logger.info(f"Processing document: {len(content)} chars, metadata: {metadata}")
            valid_documents.append(doc)

        if not valid_documents:
            logger.warning("No valid documents to add")
            return

        # Add valid documents to the assistant
        try:
            self.rag_assistant.add_documents(valid_documents)
            logger.info(f"Successfully added {len(valid_documents)} valid documents")
        except Exception as e:
            logger.error(f"Failed to add documents to RAG assistant: {e}")
            # Try to add them one by one to identify problematic documents
            for i, doc in enumerate(valid_documents):
                try:
                    self.rag_assistant.add_documents([doc])
                except Exception as doc_e:
                    logger.error(f"Failed to add document {i}: {doc_e}")
                    logger.error(f"Document content preview: {doc.get('content', '')[:200]}...")

    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        query_embedding = self.embedder.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        return [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(results['documents'][0], results['metadatas'][0])
        ]

    def invoke(self, query: str, history: List[Dict] = None) -> str:
        """Generate a response using retrieved documents and prompt guidelines."""
        # Get the general assistant prompt
        prompt = prompts.get('general_assistant_prompt', '')

        # Simple retrieval-based response
        results = self.similarity_search(query, k=3)

        if not results:
            return "I'm sorry, that information is not currently available. Please contact the council directly."

        # Combine retrieved content
        context = "\n".join([doc["content"][:500] for doc in results])

        # Format response according to prompt guidelines
        response = f"Based on the available information:\n\n{context[:1000]}"

        # Add contact information if relevant
        contact_info = prompts.get('contact_information', '')
        if contact_info and 'contact' in query.lower():
            response += f"\n\n{contact_info}"

        return response

class RAGTool:
    """Tool for retrieving civic data using RAG with optional web scraping."""

    def __init__(self):
        self.rag_assistant = None
        self.web_scraper = WebScraperTool()
        self.web_data_cache = {}  # Cache for web data
        logger.info("RAG Tool initialized")

    def _initialize_assistant(self):
        """Lazy initialization of RAG assistant."""
        if self.rag_assistant is None:
            logger.info("Initializing RAG Assistant...")
            if USE_EXISTING_RAG:
                self.rag_assistant = RAGAssistant()
                documents = load_documents()
                self.rag_assistant.add_documents(documents)
                logger.info(f"RAG Assistant ready with {len(documents)} documents")
            else:
                self.rag_assistant = SimpleRAGAssistant()
                # Load static documents
                self._load_static_documents()
                logger.info("Simple RAG Assistant ready")

    def _load_static_documents(self):
        """Load static documents from data directory."""
        data_dir = project_root / "data"
        documents = []

        logger.info(f"Loading documents from: {data_dir}")
        if data_dir.exists():
            for file_path in data_dir.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        logger.info(f"Loaded {file_path.name}: {len(content)} characters")
                        if content.strip():  # Only add non-empty documents
                            documents.append({
                                "content": content,
                                "metadata": {
                                    "source": "static",
                                    "filename": file_path.name,
                                    "type": "text_file"
                                }
                            })
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {e}")

        logger.info(f"Found {len(documents)} non-empty documents")
        if documents:
            self.rag_assistant.add_documents(documents)
            logger.info(f"Loaded {len(documents)} static documents")

    def _fetch_web_data(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetch comprehensive data from Masvingo City website."""
        cache_key = "masvingo_city_comprehensive"
        current_time = time.time()

        # Check cache (cache for 6 hours for comprehensive data)
        if not force_refresh and cache_key in self.web_data_cache:
            cached_data, timestamp = self.web_data_cache[cache_key]
            if current_time - timestamp < 21600:  # 6 hours
                logger.info("Using cached comprehensive web data")
                return cached_data

        logger.info("Fetching fresh comprehensive web data from Masvingo City website")
        try:
            web_documents = self.web_scraper.scrape_comprehensive()
            
            if web_documents:
                # Convert to document format (already in correct format)
                logger.info(f"Successfully scraped {len(web_documents)} web documents")
                
                # Cache the data
                self.web_data_cache[cache_key] = (web_documents, current_time)
                return web_documents
            else:
                logger.warning("No web documents scraped, using cache if available")
                return self.web_data_cache.get(cache_key, ([], 0))[0]
        except Exception as e:
            logger.error(f"Error fetching comprehensive web data: {e}")
            return self.web_data_cache.get(cache_key, ([], 0))[0]

    def retrieve(self, query: str, top_k: int = 5, include_web: bool = True) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query, optionally including web data."""
        self._initialize_assistant()
        logger.info(f"Retrieving documents for query: {query} (web: {include_web})")

        try:
            results = []

            # Get results from static documents
            if hasattr(self.rag_assistant, 'vector_db') and hasattr(self.rag_assistant.vector_db, 'similarity_search'):
                # Existing RAG system
                static_results = self.rag_assistant.vector_db.similarity_search(query, k=top_k)
                results.extend([{"content": doc.page_content, "metadata": doc.metadata} for doc in static_results])
            elif hasattr(self.rag_assistant, 'similarity_search'):
                # Simple RAG system
                static_results = self.rag_assistant.similarity_search(query, k=top_k)
                results.extend(static_results)
            else:
                logger.warning("RAG assistant has no similarity search method")

            # Optionally include web data
            if include_web:
                web_docs = self._fetch_web_data()
                if web_docs:
                    # For web content, do simple text matching since we don't have embeddings
                    for doc in web_docs:
                        if query.lower() in doc["content"].lower():
                            results.append(doc)

            return results[:top_k]  # Return top results

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def query(self, question: str, history: List[Dict] = None, include_web: bool = True) -> str:
        """Full RAG query with generation, optionally including web data."""
        self._initialize_assistant()
        logger.info(f"Processing RAG query: {question} (web: {include_web})")

        try:
            # If including web data, fetch and add to context
            if include_web:
                web_docs = self._fetch_web_data()
                if web_docs and not USE_EXISTING_RAG:
                    # For simple RAG, add web docs temporarily
                    self.rag_assistant.add_documents(web_docs)
                    logger.info("Added web data to RAG assistant")

            answer = self.rag_assistant.invoke(question, history=history or [])
            return answer

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return "Sorry, I couldn't process your query."