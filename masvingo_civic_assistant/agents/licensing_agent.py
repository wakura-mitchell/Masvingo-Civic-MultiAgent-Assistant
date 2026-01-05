"""
Licensing Agent - Collects user details and fills out official licence forms.
"""

from config.logging_config import logger
from tools.form_tool import FormTool
from tools.email_tool import EmailTool
from typing import Dict, Any
import yaml
from pathlib import Path

class LicensingAgent:
    """Agent for handling licensing applications."""

    def __init__(self):
        self.form_tool = FormTool()
        self.email_tool = EmailTool()

        # Load prompt configuration
        prompt_config_path = Path(__file__).parent.parent / "config" / "prompt_config.yaml"
        try:
            with open(prompt_config_path, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load prompt config: {e}")
            self.prompts = {}

        logger.info("Licensing Agent initialized")

    def handle_query(self, query: str) -> str:
        """Process a licensing query."""
        logger.info(f"Processing licensing query: {query}")
        query_lower = query.lower()

        try:
            if "apply" in query_lower or "licence" in query_lower or "license" in query_lower:
                return self._handle_licence_application(query)
            elif "form" in query_lower:
                return self._handle_form_request()
            else:
                return "I can help you apply for business licences. Please specify what type of licence you need (e.g., shop licence, trading licence)."
        except Exception as e:
            logger.error(f"Error processing licensing query: {e}")
            return "Sorry, I encountered an error processing your licensing request."

    def _handle_licence_application(self, query: str) -> str:
        """Handle licence application."""
        # Extract licence type
        licence_type = self._extract_licence_type(query)

        # For demo, collect basic info (in real implementation, this would be interactive)
        applicant_data = self._collect_applicant_info()

        # Fill form
        form_result = self.form_tool.fill_licence_form(applicant_data)

        # Send email (optional)
        email_sent = self._send_licence_email(applicant_data, form_result)

        response = f"""
**Licence Application Submitted Successfully**

**Application Details:**
- Licence Type: {licence_type}
- Applicant: {applicant_data['applicant_name']}
- National ID: {applicant_data['national_id']}
- Business Type: {applicant_data['business_type']}

**Form Status:**
- Form Generated: ✅
- Email Sent: {'✅' if email_sent else '❌'}

**Next Steps:**
1. Review the generated form PDF
2. Submit the physical copy to the council offices
3. Pay the required fees
4. Wait for approval (typically 7-14 business days)

For any questions, contact the Licensing Department at licensing@masvingo.gov.zw or +263-987-654-321.
"""

        return response.strip()

    def _handle_form_request(self) -> str:
        """Handle form download request."""
        template_path = self.form_tool.get_form_template()
        return f"You can download the licence application form template from: {template_path}"

    def _collect_applicant_info(self) -> Dict[str, Any]:
        """Collect applicant information (demo data)."""
        # In a real implementation, this would collect from user input
        return {
            "applicant_name": "John Doe",
            "national_id": "63-1234567-89",
            "address": "123 Main Street, Masvingo",
            "phone": "+263-77-123-4567",
            "email": "john.doe@example.com",
            "business_type": "Retail Shop",
            "licence_type": "Shop Licence",
            "location": "CBD, Masvingo"
        }

    def _extract_licence_type(self, query: str) -> str:
        """Extract licence type from query."""
        query_lower = query.lower()

        if "shop" in query_lower:
            return "Shop Licence"
        elif "trading" in query_lower:
            return "Trading Licence"
        elif "business" in query_lower:
            return "Business Licence"
        else:
            return "General Business Licence"

    def _send_licence_email(self, applicant_data: Dict[str, Any], form_result: str) -> bool:
        """Send licence confirmation email."""
        try:
            subject = "Licence Application Confirmation - Masvingo City Council"
            body = f"""
Dear {applicant_data['applicant_name']},

Your licence application has been submitted successfully.

Application Details:
- Licence Type: {applicant_data['licence_type']}
- Submission Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

{form_result}

Please keep this email for your records.

Best regards,
Masvingo City Council Licensing Department
"""

            return self.email_tool.send_email(
                to=applicant_data['email'],
                subject=subject,
                body=body
            )
        except Exception as e:
            logger.error(f"Failed to send licence email: {e}")
            return False