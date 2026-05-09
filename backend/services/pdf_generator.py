import base64
import io
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether
)

BLUE = colors.HexColor("#2563eb")
GREEN = colors.HexColor("#10b981")
DARK = colors.HexColor("#111827")
MUTED = colors.HexColor("#6b7280")
LIGHT = colors.HexColor("#f3f4f6")
BORDER = colors.HexColor("#d1d5db")

def _clean_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]*)`", r"<font name='Courier'>\1</font>", text)
    return text

def _footer(canvas, doc):
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(BORDER)
    canvas.line(0.7 * inch, 0.45 * inch, width - 0.7 * inch, 0.45 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.7 * inch, 0.28 * inch, "Automated Data Analysis Report")
    canvas.drawRightString(width - 0.7 * inch, 0.28 * inch, f"Page {doc.page}")
    canvas.restoreState()

def _chart_payload(value):
    if isinstance(value, dict):
        return value.get("title", "Chart"), value.get("caption", ""), value.get("image")
    return "Chart", "", value

def generate_pdf_report(summary_dict: dict, charts: dict, ai_insights: str, report_title: str = "Automated Data Analysis Report") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("ReportTitle", parent=styles["Title"], fontSize=20, textColor=colors.white, leading=28, alignment=TA_CENTER))
    styles.add(ParagraphStyle("SectionTitle", parent=styles["Heading2"], fontSize=16, textColor=DARK, spaceBefore=10, spaceAfter=10))
    styles.add(ParagraphStyle("SmallMuted", parent=styles["BodyText"], fontSize=9, textColor=MUTED, leading=12))
    styles.add(ParagraphStyle("VisualSectionTitle",parent=styles["Heading1"],fontSize=26,textColor=colors.HexColor("#7c3aed"),leading=32,alignment=TA_CENTER,spaceBefore=8,spaceAfter=20,))
    styles.add(ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=14, spaceAfter=7))
    styles.add(ParagraphStyle("ReportBullet", parent=styles["BodyText"], fontSize=10.5, leading=14, leftIndent=14, firstLineIndent=-8, spaceAfter=5))
    styles.add(ParagraphStyle("ChartCaption", parent=styles["BodyText"], fontSize=9, textColor=MUTED, leading=12, spaceAfter=8))
    styles.add(ParagraphStyle("ChartTitle",parent=styles["Heading3"],fontSize=14,textColor=DARK,spaceBefore=8,spaceAfter=4,))


    story = []
    cover = Table(
        [
            [Paragraph(report_title, styles["ReportTitle"])],
            [Paragraph(
                f"Generated on {datetime.now().strftime('%d %b %Y')}",
                ParagraphStyle("ReportDate", fontSize=10, textColor=colors.white, alignment=TA_CENTER)
            )],
        ],
        colWidths=[doc.width],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BLUE),
            ("BOX", (0, 0), (-1, -1), 0, BLUE),
            ("TOPPADDING", (0, 0), (-1, 0), 24),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 22),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]),
    )

    story.append(cover)
    story.append(Spacer(1, 0.25 * inch))

    rows = summary_dict.get("num_rows", 0)
    cols = summary_dict.get("num_cols", 0)
    missing = summary_dict.get("total_missing_values", sum(summary_dict.get("missing_values", {}).values()))
    duplicates = summary_dict.get("duplicate_rows", 0)

    kpi_data = [
    ["Rows", rows, BLUE],
    ["Columns", cols, GREEN],
    ["Missing Values", missing, colors.HexColor("#ef4444")],
    ["Duplicate Rows", duplicates, colors.HexColor("#f97316")],
]

    kpi_cells = []
    for label, value, color in kpi_data:
        kpi_cells.append(
            Table(
                [
                    [Paragraph(
                        f"<font color='{color.hexval()}'><b>{value}</b></font>",
                        ParagraphStyle("KpiValue", fontSize=18, alignment=TA_CENTER, leading=22)
                    )],
                    [Paragraph(
                        label,
                        ParagraphStyle("KpiLabel", fontSize=8, textColor=MUTED, alignment=TA_CENTER, leading=10)
                    )],
                ],
                colWidths=[doc.width / 4 - 6],
                style=TableStyle([
                    ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ])
            )
        )

    story.append(Table(
        [kpi_cells],
        colWidths=[doc.width / 4] * 4,
        style=TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ])
    ))
    story.append(Spacer(1, 0.25 * inch))


    story.append(Paragraph("Data Overview", styles["SectionTitle"]))
    story.append(Paragraph(
        f"This dataset contains <b>{rows}</b> rows and <b>{cols}</b> columns. "
        f"Detected <b>{len(summary_dict.get('numerical_cols', []))}</b> numerical columns and "
        f"<b>{len(summary_dict.get('categorical_cols', []))}</b> categorical columns.",
        styles["Body"],
    ))

    columns_text = ", ".join(summary_dict.get("columns", [])[:30])
    if columns_text:
        story.append(Paragraph(f"<b>Columns:</b> {columns_text}", styles["SmallMuted"]))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("AI Generated Insights", styles["SectionTitle"]))

    for raw_line in ai_insights.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("##"):
            story.append(Paragraph(line.replace("#", "").strip(), styles["SectionTitle"]))
        elif line.startswith(("-", "*")):
            story.append(Paragraph(f"• {_clean_markdown(line[1:].strip())}", styles["ReportBullet"]))
        else:
            story.append(Paragraph(_clean_markdown(line), styles["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("Data Visualizations", styles["VisualSectionTitle"]))

    chart_blocks = []

    for key, value in charts.items():
        title, caption, image_b64 = _chart_payload(value)
        if not image_b64:
            continue

        img_data = base64.b64decode(image_b64)
        img_buffer = io.BytesIO(img_data)
        img = Image(img_buffer)

        max_width = 5.7 * inch
        aspect = img.drawHeight / img.drawWidth
        img.drawWidth = max_width
        img.drawHeight = min(max_width * aspect, 2.85 * inch)

        block = [
            Paragraph(title, styles["ChartTitle"]),
            Paragraph(caption, styles["ChartCaption"]) if caption else Spacer(1, 0),
            img,
            Spacer(1, 0.15 * inch),
        ]

        chart_blocks.append(KeepTogether(block))

    for index, block in enumerate(chart_blocks):
        story.append(block)

        if index % 2 == 1 and index != len(chart_blocks) - 1:
            story.append(PageBreak())


    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
