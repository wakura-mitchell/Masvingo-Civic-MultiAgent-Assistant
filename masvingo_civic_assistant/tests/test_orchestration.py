# Test orchestration

import unittest
from orchestration.graph_builder import GraphBuilder

class TestOrchestration(unittest.TestCase):

    def test_graph_builder_init(self):
        builder = GraphBuilder()
        self.assertIsNotNone(builder)

    def test_graph_build(self):
        builder = GraphBuilder()
        graph = builder.build_workflow()
        self.assertIsNotNone(graph)

    def test_process_query_billing(self):
        builder = GraphBuilder()
        result = builder.process_query("How much do I owe for water?")
        self.assertEqual(result["classification"], "billing")
        self.assertIn("Current Balance", result["response"])
        self.assertEqual(result["agent_used"], "billing")

    def test_process_query_incident(self):
        builder = GraphBuilder()
        result = builder.process_query("There's a pipe burst near the school")
        self.assertEqual(result["classification"], "incident")
        self.assertIn("Incident Report Logged", result["response"])
        self.assertEqual(result["agent_used"], "incident")

    def test_process_query_licensing(self):
        builder = GraphBuilder()
        result = builder.process_query("I want to apply for a shop licence")
        self.assertEqual(result["classification"], "licensing")
        self.assertIn("Licence Application Submitted", result["response"])
        self.assertEqual(result["agent_used"], "licensing")

    def test_process_query_unknown(self):
        builder = GraphBuilder()
        result = builder.process_query("What is the weather today?")
        self.assertEqual(result["classification"], "unknown")
        self.assertIsInstance(result["response"], str)
        self.assertTrue(len(result["response"]) > 0)
        self.assertEqual(result["agent_used"], "unknown")

if __name__ == '__main__':
    unittest.main()