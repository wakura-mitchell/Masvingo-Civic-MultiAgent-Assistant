"""
Math Tool - Fee/bill calculations.
"""

from typing import Dict, Any
from config.logging_config import logger

class MathTool:
    """Tool for mathematical calculations."""

    def __init__(self):
        logger.info("Math Tool initialized")

    def calculate_fee(self, base_fee: float, penalty_rate: float = 0.1, days_overdue: int = 0) -> Dict[str, Any]:
        """Calculate total fee with penalty."""
        penalty = base_fee * penalty_rate * max(0, days_overdue // 30)  # Penalty per month
        total = base_fee + penalty
        result = {
            "base_fee": base_fee,
            "penalty": penalty,
            "total": total,
            "days_overdue": days_overdue
        }
        logger.info(f"Calculated fee: {result}")
        return result

    def calculate_bill_balance(self, previous_balance: float, payments: list, charges: list) -> Dict[str, Any]:
        """Calculate current bill balance."""
        total_payments = sum(payments)
        total_charges = sum(charges)
        current_balance = previous_balance + total_charges - total_payments
        
        result = {
            "previous_balance": previous_balance,
            "total_payments": total_payments,
            "total_charges": total_charges,
            "current_balance": current_balance
        }
        logger.info(f"Calculated balance: {result}")
        return result

    def calculate_percentage(self, value: float, percentage: float) -> float:
        """Calculate percentage of a value."""
        result = value * (percentage / 100)
        logger.info(f"Calculated {percentage}% of {value}: {result}")
        return result