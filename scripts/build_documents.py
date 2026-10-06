"""Build the project report, architecture SVG and example analysis PDF."""
import csv
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.datasets import load_datasets  # noqa: E402
from src.pipeline import analyze_document  # noqa: E402
from src.pdf_fonts import register_fonts  # noqa: E402
from src.report_generator import generate_report  # noqa: E402
from src.resume_feedback import resume_feedback  # noqa: E402
from src.resume_parser import parse_document  # noqa: E402
from src.roadmap_generator import generate_roadmap  # noqa: E402

INK = colors.HexColor("#173A43")
TEAL = colors.HexColor("#087F70")
MUTED = colors.HexColor("#536C72")


def architecture():
    drawing = Drawing(720, 490)
    drawing.add(Rect(0, 0, 720, 490, fillColor=colors.HexColor("#F6F8F5"), strokeColor=None))

    def box(x, y, w, title, detail, main=False):
        drawing.add(Rect(x, y, w, 46, rx=8, ry=8, fillColor=INK if main else colors.white, strokeColor=INK if main else colors.HexColor("#CBDCD4"), strokeWidth=1))
        drawing.add(String(x + w/2, y + 28, title, textAnchor="middle", fontName="CareerSans-Bold", fontSize=11, fillColor=colors.white if main else INK))
        drawing.add(String(x + w/2, y + 12, detail, textAnchor="middle", fontName="CareerSans", fontSize=8.5, fillColor=colors.HexColor("#C6E3D8") if main else MUTED))

    def arrow(x1, y1, x2, y2):
        drawing.add(Line(x1, y1, x2, y2, strokeColor=TEAL, strokeWidth=1.4))
        if x1 == x2:
            sign = 1 if y2 > y1 else -1
            points = [x2, y2, x2-4, y2-sign*7, x2+4, y2-sign*7]
        else:
            sign = 1 if x2 > x1 else -1
            points = [x2, y2, x2-sign*7, y2-4, x2-sign*7, y2+4]
        drawing.add(Polygon(points, fillColor=TEAL, strokeColor=None))

    for y in [430, 360, 290, 220, 150, 80]:
        if y > 80:
            arrow(354, y, 354, y - 24)
    arrow(217, 453, 247, 453)
    arrow(498, 173, 461, 173)
    arrow(217, 173, 247, 173)
    arrow(354, 80, 354, 56)
    box(12, 430, 205, "Student or job seeker", "Text PDF or DOCX resume")
    box(247, 430, 214, "Streamlit session", "Upload, validate, show progress", True)
    box(247, 360, 214, "Resume parser", "Readable pages, paragraphs, tables")
    box(247, 290, 214, "Text and section processing", "Clean text, exclude personal fields")
    box(498, 290, 210, "Skill dictionary", "110 canonical skills and aliases")
    # The dictionary supplies canonical aliases to skill extraction.
    drawing.add(Line(603, 290, 603, 243, strokeColor=TEAL, strokeWidth=1.4))
    arrow(603, 243, 461, 243)
    box(247, 220, 214, "Skill extraction", "Boundary-aware, canonical evidence")
    box(12, 150, 205, "Custom job description", "Review extracted requirements")
    box(498, 150, 210, "Job-role dataset", "13 curated educational profiles")
    box(247, 150, 214, "Matching and recommendation", "Coverage + TF-IDF cosine")
    box(247, 80, 214, "Gaps and learning plan", "Prioritize missing dependencies")
    box(247, 10, 214, "Dashboard and PDF report", "Charts, feedback and next steps", True)
    drawing.add(String(16, 95, "SESSION MEMORY ONLY", fontSize=9, fontName="CareerSans-Bold", fillColor=TEAL))
    drawing.add(String(16, 77, "No candidate database", fontSize=9, fillColor=MUTED))
    drawing.add(String(16, 60, "No external AI calls", fontSize=9, fillColor=MUTED))
    drawing.add(String(16, 43, "Clear session discards analysis", fontSize=9, fillColor=MUTED))
    return drawing


def main():
    register_fonts()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Kicker", fontName="CareerSans-Bold", fontSize=9, leading=13, textColor=TEAL, spaceAfter=12))
    styles.add(ParagraphStyle(name="ProjectTitle", fontName="CareerSans-Bold", fontSize=30, leading=35, textColor=INK, spaceAfter=13))
    styles.add(ParagraphStyle(name="ProjectSubtitle", fontName="CareerSans", fontSize=16, leading=22, textColor=MUTED, spaceAfter=16))
    styles.add(ParagraphStyle(name="Body", fontName="CareerSans", fontSize=10, leading=15, textColor=INK, spaceAfter=9))
    styles.add(ParagraphStyle(name="Small", fontName="CareerSans", fontSize=8.7, leading=12, textColor=INK, spaceAfter=5))
    styles.add(ParagraphStyle(name="Section", fontName="CareerSans-Bold", fontSize=15, leading=19, textColor=INK, spaceBefore=14, spaceAfter=8, keepWithNext=True))
    story = []
    markdown = ["# CareerLens - AI Resume Analyzer and Job Recommendation System", "", "Prepared for Saksham Jadhav | 28 September 2026", ""]

    def paragraph(text, style="Body"):
        story.append(Paragraph(escape(text), styles[style]))
        markdown.extend([text, ""])

    def heading(text):
        story.append(Paragraph(escape(text), styles["Section"]))
        markdown.extend(["## " + text, ""])

    def table(headers, rows, widths):
        cells = [[Paragraph(escape(str(v)), styles["Small"]) for v in row] for row in [headers, *rows]]
        t = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0),colors.HexColor("#DCEBE4")), ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F7F4")]), ("GRID",(0,0),(-1,-1),.5,colors.HexColor("#D1DED6")), ("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),9), ("RIGHTPADDING",(0,0),(-1,-1),9), ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),7)]))
        story.append(t)
        markdown.append("| " + " | ".join(headers) + " |")
        markdown.append("| " + " | ".join("---" for _ in headers) + " |")
        markdown.extend("| " + " | ".join(map(str, row)) + " |" for row in rows)
        markdown.append("")

    paragraph("BCA MAJOR PROJECT / IMPLEMENTATION REPORT", "Kicker")
    paragraph("CareerLens", "ProjectTitle")
    paragraph("AI Resume Analyzer and\nJob Recommendation System", "ProjectSubtitle")
    paragraph("Prepared for Saksham Jadhav | 28 September 2026", "Small")
    heading("Abstract")
    paragraph("CareerLens is an NLP-based career guidance application that extracts technical skills from PDF and DOCX resumes, compares them with curated role profiles, and produces an explainable match score, skill-gap analysis and learning plan. The application uses a 110-skill dictionary, 13 role profiles, boundary-aware alias matching and a hybrid of coverage and TF-IDF cosine similarity. A Streamlit dashboard presents rankings, evidence labels, charts, section-based feedback and custom job-description comparisons. PDF reports are generated in memory. The design avoids paid APIs and permanent storage of resumes. It supports the seven modules in the supplied specification while distinguishing documented keyword alignment from ability or hiring likelihood.")
    heading("Problem statement and objectives")
    paragraph("Students may have useful experience but struggle to communicate it in terms relevant to a target role. Generic keyword tools can conceal their scoring rules and treat missing words as missing ability. This project makes the extracted evidence visible, shows required and preferred gaps separately, explains every score component, and orders learning topics around prerequisites and practical projects.")
    heading("Existing limitations and proposed system")
    paragraph("Manual comparisons are slow and inconsistent. Simple substring searches confuse related words, while opaque generated scores are difficult to verify. CareerLens uses a controlled, reviewable dataset and deterministic rules. It preserves technical punctuation, validates uploaded documents, rejects unreadable inputs with useful messages, and offers an interactive dashboard without requiring an external backend.")
    story.append(PageBreak())

    paragraph("02 / SYSTEM DESIGN", "Kicker")
    heading("Architecture and workflow")
    drawing = architecture()
    renderSVG.drawToFile(drawing, str(ROOT / "docs/architecture.svg"))
    drawing.scale(.70, .70)
    drawing.width = 504
    drawing.height = 343
    story.append(drawing)
    paragraph("Raw documents and derived results remain in session memory. Public datasets and the fitted vectorizer are shared immutable resources. Resume feedback uses the extracted sections; the numerical score uses technical skill presence only.", "Small")
    heading("Seven implemented modules")
    table(["Module", "Implemented behavior"], [
        ("1. Resume upload", "PDF/DOCX, validation, file details and replace/remove controls"),
        ("2. Extraction and cleaning", "All readable pages, DOCX paragraphs/tables, preserved technical symbols"),
        ("3. Skill extraction", "Canonical aliases, boundaries, categories and context labels"),
        ("4. Job-role dataset", "13 curated profiles and 110 skills with prerequisites"),
        ("5. Matching", "Coverage, TF-IDF cosine, deterministic ranking and top three roles"),
        ("6. Skill gaps", "Required/preferred gaps and prerequisite-first learning plan"),
        ("7. Dashboard", "Plotly charts, custom JD, feedback and PDF report download"),
    ], [126, 380])
    story.append(PageBreak())

    paragraph("03 / METHOD AND IMPLEMENTATION", "Kicker")
    heading("Matching algorithm")
    paragraph("First, aliases map to canonical skill names. Each skill becomes a binary token, so repetitions do not add weight. TF-IDF is fitted once on the 13 role profiles. For each target, the resume vector is restricted to skills in that target's core or preferred set. Cosine similarity measures the overlap between this projected vector and the role vector.")
    paragraph("Score = 75 x core coverage + 15 x preferred coverage + 10 x cosine similarity. Each input is between zero and one. A target without preferred skills uses 90 x core coverage + 10 x similarity. Scores are bounded to 0-100 and rounded to one decimal.")
    paragraph("Because the projected resume vector contains a subset of the role's identically weighted terms, cosine equals the square root of the covered proportion of squared IDF weights. Adding a relevant skill cannot lower coverage or similarity. Unrelated skills and repeated terms have no effect. This is lexical matching, not semantic comprehension or supervised hiring prediction.")
    heading("Skill gaps, learning plan and feedback")
    paragraph("A gap means a required term was not detected, not that the candidate lacks the skill. Missing core topics are ordered by learning stage, with missing prerequisites placed first. Already-detected topics are skipped and the plan ends with a role-specific project. Preferred skills are optional additions. Contextual mentions in projects or work are distinguished from bare mentions without asserting proficiency. Feedback highlights missing sections, brief project descriptions and opportunities for truthful measurable outcomes.")
    heading("Technology and deployment design")
    table(["Part", "Technology"], [("Parsing", "pypdf and python-docx"), ("NLP and matching", "Python regular expressions and scikit-learn TF-IDF/cosine"), ("Interface and charts", "Streamlit and Plotly"), ("Reports and testing", "ReportLab, Pytest, Ruff and Playwright acceptance checks"), ("Hosting preparation", "Streamlit Community Cloud, Render configuration and Docker")], [126, 380])
    paragraph("Python 3.12 is the tested runtime. No API key, database or model download is required. Launchers, pinned dependencies, a transitive lock file, a non-root Dockerfile and deployment instructions are included.", "Small")
    story.append(PageBreak())

    paragraph("04 / EVALUATION AND RESPONSIBLE USE", "Kicker")
    heading("Testing and observed results")
    summary = json.loads((ROOT / "reports/evaluation_summary.json").read_text())
    paragraph(f"The evaluation uses {summary['labelled_profiles']} manually labelled fictional profiles exported to PDF and DOCX. All {summary['evaluated_files']} documents preserved the expected normalized text and ranked the expected role first. Micro precision and recall for the explicitly labelled skill sets were both 1.00. These are small synthetic fixtures authored for this project, not an independent benchmark or estimate of real-world accuracy.")
    evaluation = list(csv.DictReader((ROOT / "reports/evaluation.csv").open(encoding="utf-8")))
    table(["Profile and format", "Expected and actual top role", "Score"], [(row["Test resume"], row["Actual top role"], row["Top score"] + "%") for row in evaluation[:6]], [153, 283, 70])
    paragraph("Automated checks cover extraction, bad files, aliases, false positives, score bounds and monotonicity, protected-field counterfactuals, roadmaps, reports and Streamlit flows. The exact automated/browser counts and execution limitations are recorded in docs/VERIFICATION.md and the machine-readable reports.", "Small")
    heading("Privacy and responsible AI")
    paragraph("Gender, age, religion, nationality, photographs, marital status and disability are not scoring features. Recognized personal fields and sections are excluded before matching. The app makes no hiring or rejection decisions and states that absent keywords do not establish absent ability. Uploads and outputs are held in session memory, with no candidate database or external AI calls. The clear-session control discards application references; this is not a secure-memory-erasure guarantee.")
    heading("Limitations, future scope and conclusion")
    paragraph("The supported scope is readable English technical resumes. Scanned images require OCR, complex layouts may change reading order, and a controlled dictionary cannot infer every synonym or skill level. Curated role requirements vary from real vacancies. Future work should begin with consented, independently labelled evaluation, reviewed aliases, isolated OCR and measured semantic retrieval. Within its stated scope, CareerLens provides an inspectable workflow from resume upload to role comparison, skill gaps, practical next steps and a downloadable report.")
    paragraph("References: supplied project specification; official Streamlit, pypdf, python-docx, scikit-learn and Docker documentation. Full links and technical explanation are in README.md.", "Small")

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D1DED6"))
        canvas.line(44, 35, 551, 35)
        canvas.setFillColor(MUTED)
        canvas.setFont("CareerSans", 8)
        canvas.drawString(44, 23, "CAREERLENS | Major project report")
        canvas.drawRightString(551, 23, str(document.page))
        canvas.restoreState()

    SimpleDocTemplate(str(ROOT / "docs/CareerLens_Project_Report.pdf"), pagesize=(595.28, 841.89), leftMargin=44, rightMargin=44, topMargin=38, bottomMargin=48, title="CareerLens - AI Resume Analyzer and Job Recommendation System", author="Saksham Jadhav").build(story, onFirstPage=footer, onLaterPages=footer)
    (ROOT / "docs/PROJECT_REPORT.md").write_text("\n".join(markdown), encoding="utf-8")
    dictionary, roles = load_datasets()
    source = ROOT / "sample_resumes/data_analyst.pdf"
    analysis = analyze_document(parse_document(source.name, source.read_bytes()))
    target = next(r for r in analysis.rankings if r.role.name == "Machine Learning Engineer")
    roadmap = generate_roadmap(target, {s.name for s in analysis.skills}, dictionary)
    feedback = resume_feedback(analysis.sections, analysis.cleaned_text, target)
    (ROOT / "reports/Example_Analysis.pdf").write_bytes(generate_report(analysis, target, roadmap, feedback))
    print("Created project report, editable report text, architecture SVG and example analysis PDF.")


if __name__ == "__main__":
    main()
