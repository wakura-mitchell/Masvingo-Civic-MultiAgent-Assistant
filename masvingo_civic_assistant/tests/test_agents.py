# Test agents

import unittest
from agents.billing_agent import BillingAgent
from agents.incident_agent import IncidentAgent
from agents.licensing_agent import LicensingAgent
from agents.coordinator_agent import CoordinatorAgent

class TestAgents(unittest.TestCase):

    def test_billing_agent_init(self):
        agent = BillingAgent()
        self.assertIsNotNone(agent)

    def test_billing_agent_balance_query(self):
        agent = BillingAgent()
        response = agent.handle_query("How much do I owe for water?")
        self.assertIn("Current Balance", response)

    def test_incident_agent_init(self):
        agent = IncidentAgent()
        self.assertIsNotNone(agent)

    def test_incident_agent_report(self):
        agent = IncidentAgent()
        response = agent.handle_query("There's a burst pipe near Mucheke High.")
        self.assertIn("Incident Report Logged", response)

    def test_licensing_agent_init(self):
        agent = LicensingAgent()
        self.assertIsNotNone(agent)

    def test_licensing_agent_application(self):
        agent = LicensingAgent()
        response = agent.handle_query("I want to apply for a shop licence.")
        self.assertIn("Licence Application Submitted", response)

    def test_coordinator_agent_init(self):
        agent = CoordinatorAgent()
        self.assertIsNotNone(agent)

    def test_coordinator_agent_routing(self):
        agent = CoordinatorAgent()
        # Test billing
        response = agent.route_query("How much do I owe?")
        self.assertIn("Current Balance", response)
        # Test incident
        response = agent.route_query("Pipe burst in Mucheke")
        self.assertIn("Incident Report Logged", response)
        # Test licensing
        response = agent.route_query("Apply for licence")
        self.assertIn("Licence Application Submitted", response)
        # Test unknown
        response = agent.route_query("What is the weather?")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

if __name__ == '__main__':
    unittest.main()