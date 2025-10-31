#!/usr/bin/env python3
"""
Generate PDF docs from Markdown sources with a minimal renderer using reportlab.
Currently converts docs/SOW.md -> docs/SOW.pdf.
"""

import os
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER


def md_to_story(md_lines: List[str]):
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(name="H1", parent=styles["Heading1"], alignment=TA_CENTER, spaceAfter=12)
    h2 = ParagraphStyle(name="H2", parent=styles["Heading2"], spaceAfter=8)
    h3 = ParagraphStyle(name="H3", parent=styles["Heading3"], spaceAfter=6)
    body = styles["BodyText"]

    story = []
    bullets: List[str] = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            items = [ListItem(Paragraph(b, body), leftIndent=12) for b in bullets]
            story.append(ListFlowable(items, bulletType='bullet', bulletColor=colors.black, leftIndent=18))
            story.append(Spacer(1, 8))
            bullets = []

    for raw in md_lines:
        line = raw.rstrip("\n")
        if not line.strip():
            flush_bullets()
            story.append(Spacer(1, 6))
            continue
        if line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(line[2:].strip(), h1))
            continue
        if line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(line[3:].strip(), h2))
            continue
        if line.startswith("### "):
            flush_bullets()
            story.append(Paragraph(line[4:].strip(), h3))
            continue
        if line.lstrip().startswith("- "):
            bullets.append(line.lstrip()[2:].strip())
            continue
        # paragraph
        flush_bullets()
        story.append(Paragraph(line, body))
    flush_bullets()
    return story


def main():
    base = os.path.dirname(os.path.dirname(__file__))
    md_path = os.path.join(base, "docs", "SOW.md")
    pdf_path = os.path.join(base, "docs", "SOW.pdf")
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    story = md_to_story(lines)
    doc = SimpleDocTemplate(pdf_path, pagesize=LETTER, leftMargin=0.8*inch, rightMargin=0.8*inch, topMargin=0.8*inch, bottomMargin=0.8*inch)
    doc.build(story)
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()

