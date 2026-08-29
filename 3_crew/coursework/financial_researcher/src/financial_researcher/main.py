#!/usr/bin/env python
import os
import re
import sys
import warnings

from datetime import datetime
from pathlib import Path

import markdown as md
from xhtml2pdf import pisa

from financial_researcher.crew import FinancialResearcher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# --- Traditional Chinese PDF export -------------------------------------------
# Microsoft JhengHei (微軟正黑體) ships with Windows. xhtml2pdf only resolves
# font families listed in its DEFAULT_FONT table, and its @font-face loader is
# broken on Windows (it hands reportlab a still-open temp file), so we register
# the TTCs directly with reportlab and advertise both faces in the table.


def _register_cjk_fonts() -> str:
    """Register Traditional Chinese fonts for xhtml2pdf; returns the family name."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from xhtml2pdf.default import DEFAULT_FONT

    fonts_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    regular, bold = fonts_dir / "msjh.ttc", fonts_dir / "msjhbd.ttc"
    pdfmetrics.registerFont(TTFont("JhengHei", str(regular), subfontIndex=0))
    pdfmetrics.registerFont(TTFont("JhengHei-Bold", str(bold), subfontIndex=0))
    DEFAULT_FONT["jhenghei"] = "JhengHei"
    DEFAULT_FONT["jhenghei-bold"] = "JhengHei-Bold"
    return "JhengHei"


_CJK_FAMILY = _register_cjk_fonts()
_CJK_BOLD = _CJK_FAMILY + "-Bold"

_PDF_CSS = """
@page {{ size: A4; margin: 1.8cm; }}
body {{
    font-family: {family};
    font-size: 11pt;
    line-height: 1.7;
    text-align: justify;
    color: #1f2933;
    -pdf-word-wrap: CJK;
}}
h1 {{
    font-family: {bold};
    font-size: 20pt;
    color: #123c6b;
    border-bottom: 3px solid #123c6b;
    padding-bottom: 6px;
    margin-bottom: 14px;
}}
h2 {{
    font-family: {bold};
    font-size: 14pt;
    color: #123c6b;
    border-bottom: 1px solid #c3d3e5;
    padding-bottom: 3px;
    margin-top: 18px;
}}
h3 {{
    font-family: {bold};
    font-size: 12pt;
    color: #2e6da4;
    margin-top: 14px;
}}
strong, b {{ font-family: {bold}; }}
.hl {{
    font-family: {bold};
    color: #8a4b00;
    background-color: #ffe89b;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 10pt;
}}
th {{
    font-family: {bold};
    background-color: #dbe8f4;
    border: 1px solid #9db8d4;
    padding: 5px 8px;
    text-align: left;
    -pdf-word-wrap: CJK;
}}
td {{
    border: 1px solid #c3d3e5;
    padding: 5px 8px;
    -pdf-word-wrap: CJK;
}}
blockquote {{
    border-left: 4px solid #2e6da4;
    background-color: #f2f7fc;
    margin: 10px 0;
    padding: 8px 12px;
    color: #33475b;
    -pdf-word-wrap: CJK;
}}
li {{ margin-bottom: 3px; padding-right: 13px; -pdf-word-wrap: CJK; }}
code {{
    font-family: 'Courier New', monospace;
    font-size: 9.5pt;
    background-color: #f0f2f5;
}}
"""


def _export_pdf(markdown_text: str, out_dir: str = "output") -> Path:
    """Convert the markdown report to a styled Traditional Chinese PDF."""
    out_path = Path(out_dir)
    out_path.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    pdf_path = out_path / f"report_zh_{stamp}.pdf"

    # Turn ==highlight== markers into styled spans before markdown conversion
    marked = re.sub(r"==(.+?)==", r'<span class="hl">\1</span>', markdown_text, flags=re.S)

    html_body = md.markdown(marked, extensions=["extra"])
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
    {_PDF_CSS.format(family=_CJK_FAMILY, bold=_CJK_BOLD)}
</style></head>
<body>{html_body}</body></html>"""

    with open(pdf_path, "wb") as f:
        pdf = pisa.CreatePDF(html, dest=f)
    if pdf.err:
        raise RuntimeError(f"PDF conversion failed: {pdf.err}")
    return pdf_path


# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    company = input("Enter the company name for research:")
    inputs = {
        'company': company,
        'current_year': str(datetime.now().year),
        'current_date': str(datetime.now().date())
    }

    try:
        result = FinancialResearcher().crew().kickoff(inputs=inputs)
        pdf_path = _export_pdf(result.raw)
        print(f"\nReport saved to PDF: {pdf_path}")
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "company": "AI LLMs",
        'current_year': str(datetime.now().year),
        'current_date': str(datetime.now().date())
    }
    try:
        FinancialResearcher().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        FinancialResearcher().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "company": "AI LLMs",
        "current_year": str(datetime.now().year),
        "current_date": str(datetime.now().date())
    }

    try:
        FinancialResearcher().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "company": "",
        "current_year": "",
        "current_date": ""
    }

    try:
        result = FinancialResearcher().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
