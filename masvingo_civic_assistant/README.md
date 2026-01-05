# Masvingo Civic Assistant - Multi-Agent System

A mock multi-agent system extending the Council Query Assistant into a dynamic, service-oriented civic platform.

## Features

-   **Multi-Agent Architecture**: Specialized agents for billing, incidents, and licensing
-   **Tool Integration**: RAG retrieval, mock APIs, form generation, email sending
-   **Orchestration**: LangGraph-based workflows
-   **Web Interface**: Flask-based UI for both RAG and multi-agent interactions

## Setup

1. Activate the virtual environment:

    ```bash
    mcc-rag-venv\Scripts\activate
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the main script:

    ```bash
    python main.py
    ```

4. Start the web interface:
    ```bash
    python frontend/app.py
    ```

## Usage

-   Visit `http://localhost:5000` for RAG assistant
-   Visit `http://localhost:5000/agents` for multi-agent interface

## Agents

-   **Billing Agent**: Handles water bill queries
-   **Incident Agent**: Logs pipe burst reports
-   **Licensing Agent**: Fills licence forms
-   **Coordinator Agent**: Routes queries

## Tools

-   **RAG Tool**: Retrieves civic data
-   **API Tool**: Mocks Promun and Impilo APIs
-   **Form Tool**: Generates licence forms
-   **Email Tool**: Sends emails
-   **Math Tool**: Calculates fees
