#!/usr/bin/env python
import sys
import warnings

from datetime import datetime
from pathlib import Path

import markdown as md

from researcher.crew import Researcher
from xhtml2pdf import pisa

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def _export_pdf(markdown_text: str, out_dir: str = "output") -> Path:
    """Convert the markdown report to a timestamped PDF (ddmmyyyy_hhmmss) for later reference."""
    out_path = Path(out_dir)
    out_path.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    pdf_path = out_path / f"report_{stamp}.pdf"

    html_body = md.markdown(markdown_text, extensions=["extra"])
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
    @page {{ size: A4; margin: 2cm; }}
    body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.5; }}
    h1 {{ font-size: 18pt; }} h2 {{ font-size: 14pt; }} h3 {{ font-size: 12pt; }}
    pre {{ font-size: 9pt; white-space: pre-wrap; }}
    table, th, td {{ border: 1px solid #999; border-collapse: collapse; padding: 4px; }}
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
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }

    try:
        result = Researcher().crew().kickoff(inputs=inputs)
        pdf_path = _export_pdf(result.raw)
        print(f"\nReport saved to PDF: {pdf_path}")
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Researcher().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Researcher().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        Researcher().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

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
        "topic": "",
        "current_year": ""
    }

    try:
        result = Researcher().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
