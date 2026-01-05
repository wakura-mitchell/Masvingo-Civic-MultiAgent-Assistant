"""
Global Configuration Settings for Masvingo Civic Assistant

Extends the existing RAG assistant configuration with multi-agent settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT.parent / "data"  # Reuse existing data
CONFIG_DIR = PROJECT_ROOT / "config"
AGENTS_DIR = PROJECT_ROOT / "agents"
TOOLS_DIR = PROJECT_ROOT / "tools"
ORCHESTRATION_DIR = PROJECT_ROOT / "orchestration"

# API Keys (reuse existing)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Mock API Settings
PROMUN_BASE_URL = "http://localhost:8001"  # Mock server
IMPILO_BASE_URL = "http://localhost:8002"  # Mock server

# Email Settings
SMTP_SERVER = "smtp.gmail.com"  # Example; configure as needed
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Database (future SQLite)
DB_PATH = PROJECT_ROOT / "civic_assistant.db"

# Agent Settings
MAX_RETRIES = 3
TIMEOUT = 30

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = PROJECT_ROOT / "logs" / "civic_assistant.log"