"""
Coordinator Agent - Routes queries to the right agent.
"""

from config.logging_config import logger
from agents.billing_agent import BillingAgent
from agents.incident_agent import IncidentAgent
from agents.licensing_agent import LicensingAgent
import yaml
from pathlib import Path

class CoordinatorAgent:
    """Agent for routing queries to appropriate agents."""

    def __init__(self, use_langgraph: bool = True):
        self.billing_agent = BillingAgent()
        self.incident_agent = IncidentAgent()
        self.licensing_agent = LicensingAgent()
        self.use_langgraph = use_langgraph

        # Load prompt configuration
        prompt_config_path = Path(__file__).parent.parent / "config" / "prompt_config.yaml"
        try:
            with open(prompt_config_path, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load prompt config: {e}")
            self.prompts = {}

        logger.info(f"Coordinator Agent initialized (LangGraph: {use_langgraph})")

    def route_query(self, query: str) -> str:
        """Route query to the appropriate agent."""
        logger.info(f"Routing query: {query}")
        
        if self.use_langgraph:
            # Lazy import and instantiation
            from orchestration.graph_builder import GraphBuilder
            graph_builder = GraphBuilder()
            result = graph_builder.process_query(query)
            logger.info(f"LangGraph result: {result['agent_used']} -> {len(result['response'])} chars")
            return result["response"]
        else:
            # Fallback to direct routing
            return self._direct_route(query)

    def _direct_route(self, query: str) -> str:
        """Direct routing without LangGraph."""
        query_lower = query.lower()

        # Routing logic based on keywords
        if any(word in query_lower for word in ["bill", "owe", "balance", "payment", "pay"]):
            logger.info("Routing to Billing Agent")
            return self.billing_agent.handle_query(query)
        elif any(word in query_lower for word in ["burst", "pipe", "leak", "incident", "report"]):
            logger.info("Routing to Incident Agent")
            return self.incident_agent.handle_query(query)
        elif any(word in query_lower for word in ["licence", "license", "apply", "form"]):
            logger.info("Routing to Licensing Agent")
            return self.licensing_agent.handle_query(query)
        else:
            logger.info("No matching agent found")
            return self._handle_unknown_query(query)

    def _handle_unknown_query(self, query: str) -> str:
        """Handle queries that don't match any agent."""
        return """
I'm sorry, I couldn't determine which service you need. I can help with:

**Billing Services:**
- Check water bill balances
- Process payments
- View payment options

**Incident Reporting:**
- Report pipe bursts or leaks
- Log infrastructure issues

**Licensing Services:**
- Apply for business licences
- Download application forms

Please rephrase your question or specify what you need help with.
""".strip()