# Masvingo City Council RAG-Based AI Assistant

## Overview

This project is a Retrieval-Augmented Generation (RAG) AI assistant designed for the Masvingo City Council. It allows you to ask questions about council documents and get answers based on the actual content of those documents.

The backend system loads, chunks, embeds, and searches through council documents, then uses a language model to generate answers using the most relevant information found.

## Features

-   **Document Loading & Domain Classification:** Automatically assigns domain labels (by-laws, licensing, billing, notices, etc.) to documents during ingestion
-   **Structured Data Integration:** Supports loading JSON and SQL data alongside text documents
-   **Query Processing:** Classifies user queries into domains using keyword matching for targeted retrieval
-   **Domain-Based Retrieval:** Filters search results by domain for more accurate responses
-   **Retrieval Evaluation:** Built-in evaluation system with test queries, precision/recall metrics, and relevance scoring
-   **Modular Architecture:** Separate modules for ingestion, classification, retrieval, and evaluation

## How It Works

1. **Document Ingestion:** Reads text files from the `data/` directory and assigns domain labels. Also loads structured data from JSON/SQL files.
2. **Domain Classification:** Documents are categorized into domains like "by-laws", "licensing", "billing", etc.
3. **Text Chunking:** Splits each document into smaller chunks for better search and retrieval.
4. **Embedding & Storage:** Chunks are embedded and stored in a vector database (ChromaDB) with domain metadata.
5. **Query Processing:** User queries are classified into domains before retrieval.
6. **Similarity Search:** Finds the most relevant chunks using vector similarity, filtered by domain.
7. **Answer Generation:** The language model uses the retrieved context to generate a response.

## Project Structure

```
Council Query Assistant/
├── src/
│   ├── app.py                 # Main RAG application with domain classification
│   ├── vectordb.py           # Vector database wrapper
│   ├── connection.py         # Connection and setup for vector database
│   ├── embedding.py          # Embedding model loading and vectorization
│   ├── query.py              # Query logic and retrieval with domain filtering
│   ├── domain_classifier.py  # Domain classification for documents and queries
│   ├── structured_data.py    # Structured data (JSON/SQL) integration
│   ├── evaluation.py         # Retrieval evaluation system
│   ├── conversation.py       # Conversation history formatting
│   ├── utils.py              # Utility functions
│   ├── webapp.py             # Web interface
│   └── templates/
│       └── index.html        # Web UI template
├── data/                     # Council documents (.txt, .json, .db files)
├── config/
│   └── prompt_config.yaml    # Prompt configuration
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
└── README.md                 # Project guide
```

## Setup Instructions

### Prerequisites

-   Python 3.8 or higher
-   API key for your chosen LLM provider (OpenAI, Groq, Google AI, etc.)
-   This project uses Groq by default

### Installation

1. **Clone and install dependencies:**

    ```bash
    git clone [https://github.com/wakura-mitchell/Council-Query-Assistant.git]
    cd Council-Query-Assistant
    pip install -r requirements.txt
    ```

2. **Configure your API key:**

    Create a `.env` file and add your API key:

    ```
    GROQ_API_KEY=your_groq_key_here
    ```

## Usage

### Command Line Interface

1. **Run the application:**

    ```bash
    python src/app.py
    ```

2. **Available commands:**
    - `ask <question>` - Query the assistant (e.g., `ask What are the council bylaws?`)
    - `evaluate` - Run retrieval evaluation with test queries
    - `domains` - List available domains
    - `quit` - Exit the application

### Adding Data

-   **Text Documents:** Place `.txt` files in the `data/` directory. They will be automatically classified into domains based on filenames.
-   **Structured Data:** Add `.json` files or SQLite databases (`.db`, `.sqlite`) to the `data/` directory for structured data integration.

### Domain Classification

Documents are automatically classified into these domains:

-   **by-laws:** Legal documents and regulations
-   **licensing:** Permits, certifications, approvals
-   **billing:** Payment, fees, invoices
-   **notices:** Public announcements and advisories
-   **contacts:** Department contacts and office information
-   **departments:** Council department information
-   **faq:** Frequently asked questions
-   **glossary:** Terms and definitions
-   **services:** Online services and applications
-   **utilities:** Water, infrastructure services
-   **general:** General information

## Evaluation System

The system includes a comprehensive evaluation framework:

### Running Evaluation

```bash
python src/app.py
# Then type: evaluate
```

### Evaluation Metrics

-   **Precision:** Fraction of retrieved documents that are relevant
-   **Recall:** Fraction of relevant documents that are retrieved
-   **F1 Score:** Harmonic mean of precision and recall
-   **Relevance Score:** Average relevance of retrieved chunks
-   **Domain Classification Accuracy:** Accuracy of query-to-domain classification

### Test Queries

Create a `test_queries.json` file in the project root:

```json
[
	{
		"query": "What are the council bylaws?",
		"expected_domains": ["by-laws"],
		"expected_chunks": ["bylaws.txt"],
		"relevance_threshold": 0.7
	}
]
```

## API Reference

### RAGAssistant Class

```python
assistant = RAGAssistant()

# Add documents
assistant.add_documents(documents)

# Query with domain classification
answer = assistant.invoke("What are the council bylaws?", n_results=3)

# Run evaluation
results = assistant.run_evaluation(n_results=5)
```

### DomainClassifier Class

```python
classifier = DomainClassifier(use_embeddings=False)

# Classify document
domain = classifier.classify_document("bylaws.txt")

# Classify query
domain = classifier.classify_query("What are the rules?")
```

### StructuredDataHandler Class

```python
handler = StructuredDataHandler("data/")

# Load structured data
handler.load_json_files()
handler.load_sql_tables()

# Search structured data
results = handler.search_structured_data("query", domain="billing")
```

## Customization

-   **LLM Provider:** Modify `_initialize_llm()` in `app.py` to use different providers
-   **Embedding Model:** Change the model in `EmbeddingModel` class
-   **Domain Keywords:** Update `DOMAIN_KEYWORDS` in `domain_classifier.py`
-   **Chunk Size:** Adjust chunking parameters in `query.py`
-   **Evaluation Metrics:** Extend evaluation logic in `evaluation.py`

## Troubleshooting

### Common Issues

1. **No API Key Error:** Ensure your `.env` file contains a valid API key
2. **Empty Results:** Check that documents are properly loaded and chunked
3. **Low Evaluation Scores:** Review domain classification and test queries
4. **Memory Issues:** Reduce `n_results` or chunk size for large datasets

### Debug Mode

Set verbose logging in your environment:

```bash
export PYTHONPATH=src
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## License

This project is licensed under the Attribution-NonCommercial-ShareAlike 4.0 International License.
