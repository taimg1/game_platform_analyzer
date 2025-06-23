import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import navy
from fastapi import Depends
from typing import Annotated


class PdfReportService:
    def generate_game_summary_report(self, game_name: str, summary_data: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=50,
            bottomMargin=50,
            leftMargin=50,
            rightMargin=50,
        )

        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(name="Justify", alignment=TA_JUSTIFY, fontName="Helvetica")
        )

        heading1_style = styles["Heading1"]
        heading1_style.fontSize = 18
        heading1_style.alignment = TA_CENTER
        heading1_style.textColor = navy
        heading1_style.spaceAfter = 20

        heading2_style = styles["Heading2"]
        heading2_style.fontSize = 14
        heading2_style.textColor = navy
        heading2_style.spaceAfter = 10
        heading2_style.spaceBefore = 10

        story = []

        story.append(
            Paragraph(f"Market Analysis Report: {game_name}", styles["Heading1"])
        )

        sections = {
            "summary": "Overall Summary",
            "pricing_analysis": "Pricing Analysis",
            "rating_analysis": "Rating Analysis",
            "discount_analysis": "Discount Analysis",
            "conclusion": "Conclusion",
        }

        for key, title in sections.items():
            if key in summary_data and summary_data[key]:
                story.append(Paragraph(title, styles["Heading2"]))
                text = summary_data[key].replace("\n", "<br/>")
                story.append(Paragraph(text, styles["Justify"]))
                story.append(Spacer(1, 12))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


PdfReportServiceDependency = Annotated[PdfReportService, Depends(PdfReportService)]
