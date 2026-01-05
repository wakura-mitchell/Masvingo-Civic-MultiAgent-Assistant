"""
Billing Agent - Handles water bill queries and payment options.
"""

from config.logging_config import logger
from tools.api_tool import APITool
from tools.math_tool import MathTool
from typing import Dict, Any
import yaml
from pathlib import Path

class BillingAgent:
    """Agent for handling billing-related queries."""

    def __init__(self):
        self.api_tool = APITool()
        self.math_tool = MathTool()

        # Load prompt configuration
        prompt_config_path = Path(__file__).parent.parent / "config" / "prompt_config.yaml"
        try:
            with open(prompt_config_path, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load prompt config: {e}")
            self.prompts = {}

        logger.info("Billing Agent initialized")

    def handle_query(self, query: str) -> str:
        """Process a billing query."""
        logger.info(f"Processing billing query: {query}")
        query_lower = query.lower()

        try:
            if "owe" in query_lower or "balance" in query_lower or "bill" in query_lower:
                return self._handle_balance_query(query)
            elif "pay" in query_lower or "payment" in query_lower:
                if "option" in query_lower:
                    return self._handle_payment_options()
                else:
                    return self._handle_payment_query(query)
            elif "option" in query_lower:
                return self._handle_payment_options()
            else:
                return "I'm sorry, I can help with bill balances, payments, and payment options. Please rephrase your query."
        except Exception as e:
            logger.error(f"Error processing billing query: {e}")
            return "Sorry, I encountered an error processing your billing query."

    def _handle_balance_query(self, query: str) -> str:
        """Handle balance/bill queries."""
        # Extract account ID from query (simple pattern matching)
        account_id = self._extract_account_id(query)
        if not account_id:
            return "Please provide your account ID or account number to check your balance."

        # Call Promun API
        bill_data = self.api_tool.call_promun(f"/water-bill/{account_id}")

        if "error" in bill_data:
            return f"Sorry, I couldn't find billing information for account {account_id}."

        # Format response
        response = f"""
**Water Bill Information for Account {account_id}**

- Current Balance: ${bill_data['current_balance']:.2f}
- Last Payment: {bill_data['last_payment']}
- Due Date: {bill_data['due_date']}
- Status: {bill_data['status'].title()}
"""

        # Calculate if overdue
        if bill_data['current_balance'] > 0:
            response += f"\nYou have an outstanding balance. Please consider making a payment."

        return response.strip()

    def _handle_payment_query(self, query: str) -> str:
        """Handle payment processing."""
        # For demo, simulate payment
        amount = self._extract_amount(query)
        if not amount:
            return "Please specify the payment amount."

        payment_data = {
            "amount": amount,
            "method": "Paynow",  # Default
            "account_id": "DEMO123"
        }

        result = self.api_tool.call_promun("/pay-bill", "POST", payment_data)

        if result.get("status") == "success":
            return f"""
**Payment Successful!**

- Transaction ID: {result['transaction_id']}
- Amount Paid: ${result['amount_paid']:.2f}
- Payment Method: {result['payment_method']}
- Confirmation: {result['confirmation']}
"""
        else:
            return "Sorry, your payment could not be processed. Please try again."

    def _handle_payment_options(self) -> str:
        """Handle payment options query."""
        options = self.api_tool.call_promun("/payment-options")

        if "options" in options:
            response = "**Available Payment Options:**\n\n"
            for option in options["options"]:
                response += f"- **{option['name']}**: {option['description']}\n"
            return response.strip()
        else:
            return "Sorry, I couldn't retrieve payment options at this time."

    def _extract_account_id(self, query: str) -> str:
        """Extract account ID from query (simple implementation)."""
        # Look for patterns like "account 123", "ID 456", etc.
        import re
        match = re.search(r'(?:account|id)\s*(\d+)', query, re.IGNORECASE)
        return match.group(1) if match else "DEMO123"  # Default for demo

    def _extract_amount(self, query: str) -> float:
        """Extract amount from query."""
        import re
        match = re.search(r'\$?(\d+(?:\.\d{2})?)', query)
        return float(match.group(1)) if match else 0.0