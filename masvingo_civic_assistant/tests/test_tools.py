# Test tools

import unittest
from tools.rag_tool import RAGTool
from tools.api_tool import APITool
from tools.form_tool import FormTool
from tools.email_tool import EmailTool
from tools.math_tool import MathTool
from tools.web_scraper_tool import WebScraperTool

class TestTools(unittest.TestCase):

    def test_rag_tool_init(self):
        tool = RAGTool()
        self.assertIsNotNone(tool)

    def test_api_tool_promun(self):
        tool = APITool()
        result = tool.call_promun("/water-bill/12345")
        self.assertIn("current_balance", result)
        self.assertEqual(result["account_id"], "12345")

    def test_api_tool_impilo(self):
        tool = APITool()
        result = tool.call_impilo("/health-id/123456789")
        self.assertIn("registered", result)
        self.assertTrue(result["registered"])

    def test_form_tool(self):
        tool = FormTool()
        data = {"applicant_name": "John Doe", "national_id": "123456789"}
        result = tool.fill_licence_form(data)
        self.assertIn("filled", result.lower())

    def test_math_tool_fee(self):
        tool = MathTool()
        result = tool.calculate_fee(100.0, 0.1, 60)
        self.assertEqual(result["total"], 120.0)  # 100 + 10 penalty for 2 months

    def test_math_tool_balance(self):
        tool = MathTool()
        result = tool.calculate_bill_balance(50.0, [20.0, 30.0], [10.0, 15.0])
        self.assertEqual(result["current_balance"], 25.0)  # 50 + 25 - 50 = 25

    def test_web_scraper_tool_init(self):
        tool = WebScraperTool()
        self.assertIsNotNone(tool)

    def test_web_scraper_extract_text(self):
        tool = WebScraperTool()
        html = "<html><body><h1>Test</h1><p>This is a test page.</p><script>alert('test');</script></body></html>"
        text = tool.extract_text_from_html(html)
        self.assertIn("Test", text)
        self.assertIn("This is a test page", text)
        self.assertNotIn("alert", text)  # Script should be removed

if __name__ == '__main__':
    unittest.main()