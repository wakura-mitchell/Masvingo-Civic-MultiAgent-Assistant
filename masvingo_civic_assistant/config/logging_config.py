"""
Logging Configuration for Masvingo Civic Assistant
"""

import logging
import sys
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_FILE

# Create logs directory if it doesn't exist
LOG_FILE.parent.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger("masvingo_civic_assistant")