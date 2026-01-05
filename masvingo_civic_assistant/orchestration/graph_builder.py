"""
Graph Builder - LangGraph orchestration logic.
"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from config.logging_config import logger

class CivicState(TypedDict):
    """State for the civic assistant workflow."""
    query: str
    classification: Literal["billing", "incident", "licensing", "unknown"]
    response: str
    agent_used: str

class GraphBuilder:
    """Builds LangGraph workflows for agent orchestration."""

    def __init__(self):
        # Import here to avoid circular dependency
        from agents.billing_agent import BillingAgent
        from agents.incident_agent import IncidentAgent
        from agents.licensing_agent import LicensingAgent
        from tools.rag_tool import RAGTool
        
        self.billing_agent = BillingAgent()
        self.incident_agent = IncidentAgent()
        self.licensing_agent = LicensingAgent()
        self.rag_tool = RAGTool()
        
        logger.info("Graph Builder initialized")

    def build_workflow(self):
        """Build the orchestration graph."""
        logger.info("Building LangGraph workflow")

        # Create the graph
        workflow = StateGraph(CivicState)

        # Add nodes
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("billing_agent", self._billing_agent_node)
        workflow.add_node("incident_agent", self._incident_agent_node)
        workflow.add_node("licensing_agent", self._licensing_agent_node)
        workflow.add_node("unknown_handler", self._unknown_handler)

        # Add edges
        workflow.add_edge(START, "classify_query")

        # Conditional edges from classification
        workflow.add_conditional_edges(
            "classify_query",
            self._route_based_on_classification,
            {
                "billing": "billing_agent",
                "incident": "incident_agent",
                "licensing": "licensing_agent",
                "unknown": "unknown_handler"
            }
        )

        # All agent nodes go to END
        workflow.add_edge("billing_agent", END)
        workflow.add_edge("incident_agent", END)
        workflow.add_edge("licensing_agent", END)
        workflow.add_edge("unknown_handler", END)

        # Compile the graph
        self.graph = workflow.compile()
        logger.info("LangGraph workflow built successfully")
        return self.graph

    def build_workflow(self):
        """Build the orchestration graph."""
        logger.info("Building LangGraph workflow")

        # Create the graph
        workflow = StateGraph(CivicState)

        # Add nodes
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("billing_agent", self._billing_agent_node)
        workflow.add_node("incident_agent", self._incident_agent_node)
        workflow.add_node("licensing_agent", self._licensing_agent_node)
        workflow.add_node("unknown_handler", self._unknown_handler)

        # Add edges
        workflow.add_edge(START, "classify_query")

        # Conditional edges from classification
        workflow.add_conditional_edges(
            "classify_query",
            self._route_based_on_classification,
            {
                "billing": "billing_agent",
                "incident": "incident_agent",
                "licensing": "licensing_agent",
                "unknown": "unknown_handler"
            }
        )

        # All agent nodes go to END
        workflow.add_edge("billing_agent", END)
        workflow.add_edge("incident_agent", END)
        workflow.add_edge("licensing_agent", END)
        workflow.add_edge("unknown_handler", END)

        # Compile the graph
        self.graph = workflow.compile()
        logger.info("LangGraph workflow built successfully")
        return self.graph

    def _classify_query(self, state: CivicState) -> CivicState:
        """Classify the incoming query."""
        query = state["query"].lower()
        logger.info(f"Classifying query: {query}")

        # Simple keyword-based classification
        if any(word in query for word in ["bill", "owe", "balance", "payment", "pay"]):
            classification = "billing"
        elif any(word in query for word in ["burst", "pipe", "leak", "incident", "report"]):
            classification = "incident"
        elif any(word in query for word in ["licence", "license", "apply", "form"]):
            classification = "licensing"
        else:
            classification = "unknown"

        logger.info(f"Query classified as: {classification}")
        return {
            **state,
            "classification": classification
        }

    def _route_based_on_classification(self, state: CivicState) -> str:
        """Route to appropriate agent based on classification."""
        return state["classification"]

    def _billing_agent_node(self, state: CivicState) -> CivicState:
        """Handle billing queries."""
        logger.info("Executing billing agent node")
        response = self.billing_agent.handle_query(state["query"])
        return {
            **state,
            "response": response,
            "agent_used": "billing"
        }

    def _incident_agent_node(self, state: CivicState) -> CivicState:
        """Handle incident queries."""
        logger.info("Executing incident agent node")
        response = self.incident_agent.handle_query(state["query"])
        return {
            **state,
            "response": response,
            "agent_used": "incident"
        }

    def _licensing_agent_node(self, state: CivicState) -> CivicState:
        """Handle licensing queries."""
        logger.info("Executing licensing agent node")
        response = self.licensing_agent.handle_query(state["query"])
        return {
            **state,
            "response": response,
            "agent_used": "licensing"
        }

    def _unknown_handler(self, state: CivicState) -> CivicState:
        """Handle unknown queries with web-enhanced search."""
        logger.info("Executing unknown handler with web-enhanced search")
        try:
            # Try to get web data for context
            web_docs = self.rag_tool._fetch_web_data(force_refresh=False)
            web_context = ""
            
            if web_docs:
                # Extract relevant content from web documents
                for doc in web_docs[:3]:  # Limit to top 3 documents
                    content = doc.get("content", "")
                    title = doc.get("metadata", {}).get("title", "Web Content")
                    if len(content) > 200:
                        web_context += f"\n\nFrom {title}:\n{content[:1000]}..."
            
            # Create a simple response using web context
            query = state["query"].lower()
            
            # Basic keyword matching for common queries
            if any(word in query for word in ["service", "services", "offer", "provide"]):
                response = f"Based on current information from the Masvingo City Council website, here are some key services:{web_context}\n\nFor specific services, please visit https://masvingocity.org.zw/ or contact the council directly."
            elif any(word in query for word in ["contact", "phone", "email", "address"]):
                response = f"Here is the contact information from the Masvingo City Council website:{web_context}\n\nMain Office: +263 (392) 262 431/4\nEmail: info@masvingocity.org.zw\nWebsite: https://masvingocity.org.zw/"
            elif any(word in query for word in ["news", "update", "announcement", "notice"]):
                response = f"Latest updates from the Masvingo City Council website:{web_context}\n\nFor the most current information, please visit https://masvingocity.org.zw/"
            else:
                response = f"I've searched the Masvingo City Council website for information related to your query.{web_context}\n\nFor more detailed assistance, please contact the council directly or visit their website."
            
            logger.info(f"Web-enhanced response generated: {len(response)} characters")
            
        except Exception as e:
            logger.error(f"Web-enhanced search failed: {e}")
            response = """
I'm sorry, I couldn't determine which service you need help with. I can assist you with:

**Billing Services:**
- Check water bill balances and payment history
- Process payments through various methods
- View billing information and due dates

**Incident Reporting:**
- Report pipe bursts, leaks, or infrastructure issues
- Log maintenance requests and emergencies

**Licensing Services:**
- Apply for business licences and permits
- Get information about licensing requirements
- Track application status

**General Information:**
- Council contact details and office locations
- Frequently asked questions
- Department information and services

Please rephrase your question or specify which service you need help with. For urgent matters, contact the Masvingo City Council directly at +263-39-123-456.
"""
        return {
            **state,
            "response": response,
            "agent_used": "unknown"
        }

    def process_query(self, query: str) -> dict:
        """Process a query through the LangGraph workflow."""
        if not hasattr(self, 'graph'):
            self.build_workflow()

        initial_state = {
            "query": query,
            "classification": "unknown",
            "response": "",
            "agent_used": ""
        }

        logger.info(f"Processing query through LangGraph: {query}")
        result = self.graph.invoke(initial_state)

        return {
            "query": result["query"],
            "classification": result["classification"],
            "response": result["response"],
            "agent_used": result["agent_used"]
        }