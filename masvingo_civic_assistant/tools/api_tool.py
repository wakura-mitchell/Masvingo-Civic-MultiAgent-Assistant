"""
API Tool - Simulates Promun and Impilo API calls.
"""

import requests
from typing import Dict, Any, List
from config.settings import PROMUN_BASE_URL, IMPILO_BASE_URL
from config.logging_config import logger

class APITool:
    """Tool for mock API interactions."""

    def __init__(self):
        logger.info("API Tool initialized")

    def call_promun(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call Promun API mock."""
        url = f"{PROMUN_BASE_URL}{endpoint}"
        logger.info(f"Calling Promun: {method} {url}")
        
        # Mock responses based on endpoint
        if endpoint.startswith("/water-bill/"):
            account_id = endpoint.split("/")[-1]
            return {
                "account_id": account_id,
                "current_balance": 150.00,
                "last_payment": "2025-12-01",
                "due_date": "2026-01-15",
                "status": "active"
            }
        elif endpoint == "/pay-bill" and method == "POST":
            # Simulate payment processing
            return {
                "status": "success",
                "transaction_id": "TXN123456789",
                "amount_paid": data.get("amount", 0),
                "payment_method": data.get("method", "unknown"),
                "confirmation": "Payment processed successfully"
            }
        elif endpoint == "/payment-options":
            return {
                "options": [
                    {"name": "Paynow", "description": "Mobile payment via Paynow"},
                    {"name": "Zikicash", "description": "Mobile payment via Zikicash"},
                    {"name": "In-person", "description": "Pay at council offices"}
                ]
            }
        else:
            return {"error": "Unknown Promun endpoint", "endpoint": endpoint}

    def call_impilo(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call Impilo API mock."""
        url = f"{IMPILO_BASE_URL}{endpoint}"
        logger.info(f"Calling Impilo: {method} {url}")
        
        # Mock responses based on endpoint
        if endpoint.startswith("/health-id/"):
            national_id = endpoint.split("/")[-1]
            return {
                "national_id": national_id,
                "registered": True,
                "clinic_info": {
                    "name": "Mucheke Health Clinic",
                    "location": "Mucheke",
                    "services": ["Health ID registration", "Basic healthcare"]
                },
                "registration_date": "2025-06-15"
            }
        elif endpoint == "/register-health-id" and method == "POST":
            # Simulate registration
            return {
                "status": "registered",
                "health_id": f"HID{data.get('national_id', 'UNKNOWN')[:6]}",
                "clinic_assigned": "Mucheke Health Clinic",
                "next_steps": "Visit clinic for biometric verification"
            }
        elif endpoint == "/clinic-locations":
            return {
                "clinics": [
                    {
                        "name": "Mucheke Health Clinic",
                        "location": "Mucheke",
                        "services": ["Health ID", "Maternal care"],
                        "contact": "+263-123-456"
                    },
                    {
                        "name": "City Center Clinic",
                        "location": "Masvingo CBD",
                        "services": ["Health ID", "Emergency care"],
                        "contact": "+263-987-654"
                    }
                ]
            }
        else:
            return {"error": "Unknown Impilo endpoint", "endpoint": endpoint}