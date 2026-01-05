"""
Email Agent - Sends completed licence forms.
"""

from config.logging_config import logger

class EmailAgent:
    """Agent for sending emails."""

    def __init__(self):
        logger.info("Email Agent initialized")

    def send_email(self, to: str, subject: str, body: str) -> str:
        """Send an email."""
        logger.info(f"Sending email to {to}: {subject}")
        return "Email Agent: This is a placeholder for sending emails."