# Masvingo City Council RAG-Based AI Assistant

## Overview

This project is a Retrieval-Augmented Generation (RAG) AI assistant designed for the Masvingo City Council. It allows you to ask questions about council documents and get answers based on the actual content of those documents.

The backend system loads, chunks, embeds, and searches through council documents, then uses a language model to generate answers using the most relevant information found.

## Features

-   Load and process council documents from the `data/` directory
-   Chunk documents for efficient retrieval
-   Store and search document chunks in a vector database (ChromaDB)
-   Generate answers using retrieved context and a language model

## How It Works

1. **Document Loading:** Reads all text files from the `data/` directory and loads their content into memory.
2. **Text Chunking:** Splits each document into smaller chunks for better search and retrieval.
3. **Document Ingestion:** Chunks are embedded and stored in a vector database for fast similarity search.
4. **Similarity Search:** When you ask a question, the system finds the most relevant chunks using vector similarity.
5. **Answer Generation:** The language model uses the retrieved context to generate a response to your question.

## Setup Instructions

### Prerequisites

-   Python 3.8 or higher
-   API key for your chosen LLM provider (OpenAI, Groq, Google AI, etc.)
-   This project used Groq

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
    OPENAI_API_KEY=your_key_here
    # OR
    GROQ_API_KEY=your_key_here
    # OR
    GOOGLE_API_KEY=your_key_here
    ```

## Usage

1. Add your council documents or any document that you might want (as `.txt` files) to the `data/` directory.
2. Run the backend application:

    ```bash
    python src/app.py
    ```

3. Ask questions about the council documents and receive answers based on their content.

## Project Structure

```
Council Query Assistant/
├── src/
│   ├── app.py           # Main RAG application
│   ├── vectordb.py      # Vector database wrapper
│   ├── connection.py    # Connection and setup for vector database
│   ├── embedding.py     # Embedding model loading and vectorization
│   ├── query.py         # Query logic and retrieval from the vector db.
├── data/                # Council documents (.txt files)
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── README.md            # Project guide
```

## Customization

You can use alternative vector databases, embedding models, or LLM providers as needed. The backend is modular and can be extended for other document types or domains.

## License

This project is licensed under the Attribution-NonCommercial-ShareAlike 4.0 International License.
