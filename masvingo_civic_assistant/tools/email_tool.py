"""
Email Tool - SMTP/email sender.
"""

import smtplib
from email.mime.text import MIMEText
from config.settings import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from config.logging_config import logger

class EmailTool:
    """Tool for sending emails."""

    def __init__(self):
        logger.info("Email Tool initialized")

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email."""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = SMTP_USERNAME
            msg['To'] = to

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to, msg.as_string())
            server.quit()
            logger.info(f"Email sent to {to}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False