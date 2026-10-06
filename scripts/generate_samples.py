"""Rebuild the fictional test resumes in both supported formats."""
from pathlib import Path
import sys
from xml.sax.saxutils import escape

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.pdf_fonts import register_fonts  # noqa: E402
SAMPLES = {
    "data_analyst": [
        ("Synthetic Data Analyst Resume", "Fictional sample for CareerLens testing. No real personal information."),
        ("Summary", "Entry-level analyst focused on cleaning structured datasets and communicating useful business findings."),
        ("Technical Skills", "Python, SQL, Excel, Pandas, Power BI, Statistics, Data Visualization, Data Cleaning."),
        ("Education", "Bachelor of Computer Applications, Sample Institute, 2026. Coursework in databases and applied statistics."),
        ("Academic Projects", "Retail reporting: cleaned 12000 synthetic sales records using Python and Pandas. Queried customer segments in SQL and reconciled results against Excel totals. Built a Power BI dashboard with monthly trends, filters and clear chart labels. Documented data cleaning rules and reviewed the results with a project teammate."),
        ("Internships", "Sample analytics lab: used statistics and data visualization to summarize category-level changes in a fictional retail dataset. Reviewed source totals before sharing the report."),
        ("Certifications", "Completed an introductory spreadsheet analysis course in a fictional training program."),
    ],
    "ml_engineer": [
        ("Synthetic ML Engineer Resume", "Fictional sample for CareerLens testing. No real personal information."),
        ("Professional Summary", "Early-career machine learning practitioner building reproducible training and inference workflows."),
        ("Core Skills", "Python, Machine Learning, scikit-learn, FastAPI, Docker, Pandas, SQL, Model Evaluation, Git, Unit Testing."),
        ("Education", "Bachelor of Computer Science, Sample Institute, 2026. Coursework in algorithms, databases and probability."),
        ("Projects", "Demand classifier: prepared 8000 synthetic records in Pandas and SQL. Built a scikit-learn preprocessing and machine learning pipeline, separated validation and test data, and documented model evaluation with a confusion matrix. Served predictions through FastAPI, packaged the service with Docker, and added unit testing for invalid API inputs."),
        ("Experience", "Fictional engineering lab: used Python and Git to review preprocessing changes and reproduce model evaluation results. Wrote a setup guide and checked container startup with synthetic examples."),
        ("Certifications", "Completed a fictional introductory course in reproducible model development."),
    ],
    "nlp_engineer": [
        ("Synthetic NLP Engineer Resume", "Fictional sample for CareerLens testing. No real personal information."),
        ("Profile", "Language technology graduate interested in evaluating text processing systems and documenting model limitations."),
        ("Skills", "Python, NLP, Transformers, Hugging Face, spaCy, Text Classification, Named Entity Recognition, PyTorch, Model Evaluation."),
        ("Education", "Bachelor of Computer Science, Sample Institute, 2026. Coursework in text processing and software engineering."),
        ("Academic Projects", "Support message triage: built a text classification experiment on 6000 synthetic messages using Python, NLP, Transformers and Hugging Face. Compared tokenization settings and recorded model evaluation on a held-out split. Used spaCy for named entity recognition and reviewed false positives. Reproduced a small PyTorch experiment with fixed seeds and saved the evaluation configuration."),
        ("Internship Experience", "Fictional language lab: annotated text examples, reviewed disagreement cases and documented errors in the NLP pipeline. Wrote a report explaining where transformer predictions were unreliable."),
        ("Achievements", "Presented the fictional text processing study at a classroom demonstration."),
    ],
}


def main():
    register_fonts()
    folder = ROOT / "sample_resumes"
    folder.mkdir(exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SampleTitle", fontName="CareerSans-Bold", fontSize=20, leading=25, textColor=colors.HexColor("#173A43"), spaceAfter=10))
    styles["BodyText"].fontName = "CareerSans"
    styles["Heading2"].fontName = "CareerSans-Bold"
    styles["BodyText"].fontSize = 10
    styles["BodyText"].leading = 15
    for stem, sections in SAMPLES.items():
        doc = Document()
        doc.core_properties.author = "CareerLens synthetic fixture"
        doc.core_properties.title = sections[0][0]
        sec = doc.sections[0]
        sec.top_margin = sec.bottom_margin = Inches(.7)
        sec.left_margin = sec.right_margin = Inches(.8)
        for name in ("Normal", "Title", "Heading 1"):
            style = doc.styles[name]
            style.font.name = "Calibri"
            style.font.color.rgb = RGBColor(0, 0, 0)
        doc.styles["Normal"].font.size = Pt(10)
        doc.styles["Normal"].paragraph_format.space_after = Pt(7)
        doc.styles["Title"].font.size = Pt(22)
        doc.styles["Heading 1"].font.size = Pt(13)
        for border in doc.styles.element.xpath(".//w:pBdr"):
            border.getparent().remove(border)
        story = []
        for i, (heading, text) in enumerate(sections):
            doc.add_paragraph(heading, "Title" if i == 0 else "Heading 1")
            doc.add_paragraph(text)
            story.extend([Paragraph(escape(heading), styles["SampleTitle" if i == 0 else "Heading2"]), Paragraph(escape(text), styles["BodyText"]), Spacer(1, 6)])
        doc.save(folder / f"{stem}.docx")
        SimpleDocTemplate(str(folder / f"{stem}.pdf"), topMargin=44, bottomMargin=44, leftMargin=48, rightMargin=48, title=sections[0][0], author="CareerLens synthetic fixture").build(story)
        (folder / f"{stem}.txt").write_text("\n\n".join(h + "\n" + t for h, t in sections), encoding="utf-8")
    (folder / "custom_job.txt").write_text("Python API Developer\nRequired skills:\nPython, SQL, REST APIs, FastAPI, Docker and Unit Testing.\nBuild and maintain tested data APIs.\nPreferred skills:\nPostgreSQL and Redis.\n", encoding="utf-8")
    print("Created 3 fictional profiles in PDF, DOCX and TXT, plus a sample job description.")


if __name__ == "__main__":
    main()
