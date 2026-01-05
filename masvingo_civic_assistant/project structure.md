masvingo_civic_assistant/
│
├── README.md
├── requirements.txt
├── main.py # Entry point: runs the system
│
├── config/
│ ├── settings.py # Global configs (API keys, endpoints, constants)
│ └── logging_config.py # Logging setup
│
├── agents/
│ ├── **init**.py
│ ├── billing_agent.py # Handles water bill queries
│ ├── incident_agent.py # Handles pipe burst reports
│ ├── licensing_agent.py # Collects details, fills forms
│ ├── email_agent.py # Sends completed licence forms
│ └── coordinator_agent.py# Routes queries to the right agent
│
├── tools/
│ ├── **init**.py
│ ├── rag_tool.py # Custom RAG retrieval tool
│ ├── api_tool.py # Mock Promun & Impilo API calls
│ ├── form_tool.py # Licence form generator/filler
│ ├── email_tool.py # SMTP/email sender
│ └── math_tool.py # Fee/bill calculations
│
├── orchestration/
│ ├── **init**.py
│ ├── graph_builder.py # LangGraph orchestration logic
│
├── data/
│ ├── bylaws.txt
│ ├── licensing.txt
│ ├── water_billing.txt
│ ├── contacts.txt
│ └── notices.txt
│
├── frontend/
│ ├── **init**.py
│ ├── app.py # Flask frontend
│ ├── templates/
│ │ └── index.html # User interface
│ └── static/
│ ├── css/
│ └── js/
│
└── tests/
├── test_agents.py
├── test_tools.py
├── test_orchestration.py
└── test_frontend.py
