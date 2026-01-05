## Masvingo Civic Multi‑Agent Assistant

## Overview
The Masvingo Civic Assistant is a multi‑agent Retrieval‑Augmented Generation (RAG) system designed to improve citizen engagement with municipal services in Masvingo, Zimbabwe. It combines semantic search, structured knowledge integration, and live web scraping to deliver accurate, context‑aware responses about council services such as billing, licensing, incident reporting, and general inquiries.

Built as a production‑ready web application, the assistant demonstrates how modern AI can transform public service delivery by providing citizens with 24/7 access to municipal information through an intuitive interface.

## Features
Multi‑Agent Architecture: Specialized agents for billing, licensing, incident reporting, and general queries.

Intelligent Query Routing: LangGraph orchestration routes queries to the most appropriate agent.

Web‑Enhanced Knowledge Base: Live scraping of official council web pages ensures up‑to‑date information.

Hybrid Retrieval: Combines vector search (ChromaDB) with structured data (JSON/SQL).

Evaluation Framework: Built‑in metrics for precision, recall, F1 score, relevance, and domain classification accuracy.

Safety Measures: Domain filtering, input validation, error handling, and fallback mechanisms to prevent harmful outputs.

Production‑Ready Design: Modular architecture, error logging, environment‑specific configuration, and extensibility.

## How It Works
Web Scraping & Document Ingestion: Extracts content from official council web pages and local civic documents.

Domain Classification: Queries and documents are categorized into domains (billing, licensing, incidents, general, etc.).

Vectorization & Storage: Text is embedded using sentence transformers and stored in ChromaDB with metadata.

Query Routing: LangGraph orchestrates query flow, directing it to the correct agent.

Hybrid Retrieval: Agents pull from both vector database and structured civic records.

Response Generation: Groq API LLM generates grounded, context‑aware answers.

Fallback Handling: If an agent fails, the system provides web‑enhanced responses as backup.

## Project Structure

    Masvingo-Civic-MultiAgent-Assistant/
        ├── .env                      # Environment variables configuration
        ├── .git/                     # Git repository metadata
        ├── .gitignore                # Git ignore rules
        ├── LICENSE                   # Project license file
        ├── README.md                 # Project documentation
        ├── requirements.txt          # Python dependencies
        ├── test_queries.json          # Test queries for system validation
    
    ├── config/                   # Root configuration directory
    │   └── prompt_config.yaml    # Prompt templates and configurations
    
    ├── data/                     # Static data files for RAG system
    │   ├── about_me.txt          # Council information data
    │   ├── bill_payments.txt     # Billing and payment information
    │   ├── bylaws.txt            # Council bylaws and regulations
    │   ├── council_contacts.txt  # Contact information for departments
    │   ├── departments.txt       # Department listings and descriptions
    │   ├── faq.txt               # Frequently asked questions
    │   ├── glossary.txt          # Terminology definitions
    │   ├── new.js                # JavaScript data file
    │   ├── online_services.txt   # Online service descriptions
    │   ├── operating_licenses.txt# License and permit information
    │   ├── public_notices.txt    # Public announcements and notices
    │   └── water_distribution.txt# Water service information
    
    ├── databases/                # Vector database storage
    │   └── chroma_db/            # ChromaDB vector database files
    
    ├── mcc-rag-venv/             # Python virtual environment
    │   ├── pyvenv.cfg            # Virtual environment configuration
    │   ├── Include/              # C headers for compiled extensions
    │   ├── Lib/                  # Python packages and modules
    │   │   └── site-packages/    # Installed third-party packages
    │   └── Scripts/              # Virtual environment scripts
    
    ├── src/                      # Legacy source code directory
    │   ├── app.py                # Legacy RAG assistant implementation
    │   ├── connection.py         # Database connection utilities
    │   ├── conversation.py       # Conversation management
    │   ├── domain_classifier.py  # Query domain classification
    │   ├── embedding.py          # Text embedding utilities
    │   ├── evaluation.py         # System evaluation tools
    │   ├── query.py              # Query processing logic
    │   ├── structured_data.py    # Structured data handling
    │   ├── utils.py              # Utility functions
    │   ├── vectordb.py           # Vector database operations
    │   ├── webapp.py             # Legacy web application
    │   ├── pycache/              # Python bytecode cache
    │   └── templates/            # Legacy HTML templates
    │       └── index.html        # Legacy web interface

    └── masvingo_civic_assistant/ # Main application directory
        ├── .pytest_cache/        # Pytest cache directory
        ├── main.py               # Application entry point
        ├── project structure.md  # Project structure documentation
        ├── README.md             # Application-specific documentation
        ├── requirements.txt      # Application dependencies
        ├── Application-for-issue-of-new-licence_2.pdf # Sample license application
        ├── licence_form_John Doe.pdf                 # Generated license form sample
        ├── licence_form_Test User.pdf                # Generated license form sample

    ├── agents/               # Specialized AI agents
    │   ├── __init__.py       # Agents package initialization
    │   ├── pycache/          # Python bytecode cache
    │   ├── billing_agent.py  # Handles billing and payment queries
    │   ├── coordinator_agent.py # Coordinates multi-agent interactions
    │   ├── email_agent.py    # Manages email communications
    │   ├── incident_agent.py # Processes incident reports
    │   └── licensing_agent.py# Handles license and permit applications

    ├── config/               # Application configuration
    │   ├── pycache/          # Python bytecode cache
    │   ├── logging_config.py # Logging configuration
    │   ├── prompt_config.yaml# Agent prompt configurations
    │   └── settings.py       # Application settings

    ├── data/                 # Application data storage
    │   └── incidents.json    # Incident tracking data

    ├── databases/            # Application database storage
    │   └── chroma_db/        # ChromaDB vector database

    ├── frontend/             # Web frontend application
    │   ├── __init__.py       # Frontend package initialization
    │   ├── pycache/          # Python bytecode cache
    │   ├── app.py            # Main Flask application
    │   ├── webapp.py         # Alternative web application
    │   ├── test_frontend.py  # Frontend unit tests
    │   ├── databases/        # Frontend database storage
    │   ├── static/           # Static web assets
    │   │   ├── css/          # Stylesheets
    │   │   │   └── main.css  # Main application styles
    │   │   ├── icons/        # Application icons
    │   │   ├── js/           # JavaScript files
    │   │   ├── manifest.json # Web app manifest
    │   │   └── sw.js         # Service worker
    │   └── templates/        # HTML templates
    │       ├── index.html    # Main web interface
    │       └── agent_interface.html # Agent interaction interface

    ├── logs/                 # Application logs
    │   └── civic_assistant.log # Main application log file

    ├── orchestration/        # Multi-agent orchestration
    │   ├── __init__.py       # Orchestration package initialization
    │   ├── pycache/          # Python bytecode cache
    │   └── graph_builder.py  # LangGraph orchestration logic

    ├── tests/                # Test suite
    │   ├── pycache/          # Python bytecode cache
    │   ├── test_agents.py    # Agent unit tests
    │   ├── test_frontend.py  # Frontend unit tests
    │   ├── test_orchestration.py # Orchestration unit tests
    │   └── test_tools.py     # Tool unit tests

    └── tools/                # Utility tools and integrations
        ├── __init__.py       # Tools package initialization
        ├── pycache/          # Python bytecode cache
        ├── api_tool.py       # API interaction utilities
        ├── email_tool.py     # Email sending functionality
        ├── form_tool.py      # Form processing tools
        ├── math_tool.py      # Mathematical computation tools
        ├── rag_tool.py       # RAG system integration
        └── web_scraper_tool.py # Web scraping functionality


## Setup Instructions
### Prerequisites
- Python 3.8+

- API key for Groq (default) or other LLM provider

- Civic documents and/or council web pages for scraping

## Installation
bash
git clone https://github.com/wakura-mitchell/Masvingo-Civic-MultiAgent-Assistant.git
cd Masvingo-Civic-MultiAgent-Assistant
pip install -r requirements.txt
Configure your .env file with API keys and environment settings.

## Usage
Run the Application
bash
python app.py
Access the assistant at http://localhost:5000 and enter queries such as:

“How do I apply for a shop licence?”

“What are the water billing procedures?”

“Report a pipe burst in Ward 5.”

CLI Commands
ask <question> – Query the assistant

evaluate – Run retrieval evaluation

domains – List available domains

quit – Exit

Evaluation System
Run evaluation with test queries:

bash
python evaluation/evaluation.py
Metrics include precision, recall, F1 score, relevance, and domain classification accuracy.

## Future Enhancements
Local language NLP support

Mobile and voice interfaces

Analytics dashboard for administrators

Multi‑channel integration (social media, messaging platforms)

License
This project is licensed under the Attribution‑NonCommercial‑ShareAlike 4.0 International License.
