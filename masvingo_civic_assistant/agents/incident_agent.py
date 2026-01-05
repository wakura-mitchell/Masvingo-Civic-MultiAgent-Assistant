"""
Incident Agent - Logs pipe burst reports with location and severity.
"""

from config.logging_config import logger
from datetime import datetime
import json
import os
from pathlib import Path
import yaml

class IncidentAgent:
    """Agent for handling incident reports."""

    def __init__(self):
        self.incidents_file = Path(__file__).parent.parent / "data" / "incidents.json"
        self.incidents_file.parent.mkdir(exist_ok=True)
        if not self.incidents_file.exists():
            with open(self.incidents_file, 'w') as f:
                json.dump([], f)

        # Load prompt configuration
        prompt_config_path = Path(__file__).parent.parent / "config" / "prompt_config.yaml"
        try:
            with open(prompt_config_path, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load prompt config: {e}")
            self.prompts = {}

        logger.info("Incident Agent initialized")

    def handle_query(self, query: str) -> str:
        """Process an incident query."""
        logger.info(f"Processing incident query: {query}")
        query_lower = query.lower()

        try:
            if "burst" in query_lower or "pipe" in query_lower or "leak" in query_lower:
                return self._log_incident_report(query)
            elif "report" in query_lower and "incident" in query_lower:
                return self._log_incident_report(query)
            else:
                return "I can help you report pipe bursts, leaks, or other water infrastructure incidents. Please describe the issue with location details."
        except Exception as e:
            logger.error(f"Error processing incident query: {e}")
            return "Sorry, I encountered an error processing your incident report."

    def _log_incident_report(self, query: str) -> str:
        """Log an incident report."""
        # Extract location and severity from query
        location = self._extract_location(query)
        severity = self._extract_severity(query)

        # Create incident record
        incident = {
            "id": f"INC{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "description": query,
            "location": location,
            "severity": severity,
            "status": "reported",
            "reported_by": "user"
        }

        # Save to file
        try:
            with open(self.incidents_file, 'r') as f:
                incidents = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            incidents = []

        incidents.append(incident)

        with open(self.incidents_file, 'w') as f:
            json.dump(incidents, f, indent=2)

        logger.info(f"Incident logged: {incident['id']}")

        # Format response
        response = f"""
**Incident Report Logged Successfully**

- **Report ID**: {incident['id']}
- **Location**: {location}
- **Severity**: {severity.title()}
- **Status**: {incident['status'].title()}
- **Timestamp**: {incident['timestamp']}

Thank you for reporting this incident. Our maintenance team will investigate and address it as soon as possible. You will be updated on the progress.

For urgent situations, please also contact our emergency hotline at +263-123-456-789.
"""

        return response.strip()

    def _extract_location(self, query: str) -> str:
        """Extract location from query."""
        # Simple location extraction
        locations = ["mucheke", "cbd", "city center", "high school", "clinic", "hospital"]
        query_lower = query.lower()

        for loc in locations:
            if loc in query_lower:
                return loc.title()

        # Look for "near" or "at"
        import re
        match = re.search(r'(?:near|at|in)\s+([A-Za-z\s]+)', query, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()

        return "Location not specified"

    def _extract_severity(self, query: str) -> str:
        """Extract severity from query."""
        query_lower = query.lower()

        if any(word in query_lower for word in ["major", "severe", "critical", "emergency"]):
            return "high"
        elif any(word in query_lower for word in ["moderate", "medium", "significant"]):
            return "medium"
        elif any(word in query_lower for word in ["minor", "small", "slight"]):
            return "low"
        else:
            return "medium"  # Default

    def get_incidents(self) -> list:
        """Get all logged incidents."""
        try:
            with open(self.incidents_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []