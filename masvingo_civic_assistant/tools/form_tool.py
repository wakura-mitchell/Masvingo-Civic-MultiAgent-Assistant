"""
Form Tool - Fills and formats licence applications.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from config.logging_config import logger

class FormTool:
    """Tool for generating and filling forms."""

    def __init__(self):
        self.template_path = Path(__file__).parent.parent / "Application-for-issue-of-new-licence_2.pdf"
        logger.info("Form Tool initialized")

    def fill_licence_form(self, data: dict) -> str:
        """Fill licence application form and generate PDF."""
        logger.info(f"Filling licence form with data: {data}")
        
        # Generate a simple PDF with form data
        output_path = Path(__file__).parent.parent / f"licence_form_{data.get('applicant_name', 'unknown')}.pdf"
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Application for Issue of New Licence", styles['Title']))
        story.append(Spacer(1, 12))

        # Form fields
        fields = [
            ("Applicant Name", data.get("applicant_name", "")),
            ("National ID", data.get("national_id", "")),
            ("Address", data.get("address", "")),
            ("Phone", data.get("phone", "")),
            ("Email", data.get("email", "")),
            ("Business Type", data.get("business_type", "")),
            ("Licence Type", data.get("licence_type", "")),
            ("Location", data.get("location", "")),
        ]

        for label, value in fields:
            story.append(Paragraph(f"<b>{label}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 6))

        # Declaration
        story.append(Spacer(1, 12))
        story.append(Paragraph("I hereby declare that the information provided is true and correct.", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Signature: ____________________ Date: _______________", styles['Normal']))

        doc.build(story)
        
        logger.info(f"Licence form generated: {output_path}")
        return f"Licence form filled and saved to {output_path}"

    def get_form_template(self) -> str:
        """Get path to form template."""
        return str(self.template_path)