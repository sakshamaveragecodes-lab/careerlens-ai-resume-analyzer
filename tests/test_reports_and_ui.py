import io

from pypdf import PdfReader
from streamlit.testing.v1 import AppTest

from src.config import ROOT
from src.pipeline import analyze_document
from src.report_generator import generate_report
from src.resume_feedback import resume_feedback
from src.resume_parser import parse_document
from src.roadmap_generator import generate_roadmap


def test_pdf_report_content_and_privacy(dictionary):
    document = parse_document("data_analyst.pdf", (ROOT / "sample_resumes/data_analyst.pdf").read_bytes())
    analysis = analyze_document(document)
    target = analysis.rankings[0]
    data = generate_report(analysis, target, generate_roadmap(target, {s.name for s in analysis.skills}, dictionary), resume_feedback(analysis.sections, analysis.cleaned_text, target))
    reader = PdfReader(io.BytesIO(data))
    text = "\n".join(page.extract_text() for page in reader.pages)
    assert data.startswith(b"%PDF") and len(reader.pages) >= 2
    for expected in ["Data Analyst", "Skill alignment", "Not detected", "score", "Python", "Privacy"]:
        assert expected.lower() in text.lower()
    assert "12000 synthetic sales records" not in text


def test_streamlit_sample_target_change_report_and_clear():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not app.exception
    assert next(b for b in app.button if b.label == "Analyze resume").disabled
    next(b for b in app.button if b.label == "Try Data Analyst").click().run()
    assert not app.exception
    assert any(m.label == "Skills detected" for m in app.metric)
    app.selectbox[0].select("Machine Learning Engineer").run()
    assert not app.exception
    next(b for b in app.button if b.label == "Prepare PDF report").click().run()
    assert not app.exception and app.session_state["report"].startswith(b"%PDF")
    next(b for b in app.button if b.label == "Clear session").click().run()
    assert not app.exception and "analysis" not in app.session_state
    assert app.session_state["upload_generation"] == 1
    assert next(b for b in app.button if b.label == "Analyze resume").disabled
    next(b for b in app.button if b.label == "Clear session").click().run()
    assert app.session_state["upload_generation"] == 2


def test_streamlit_navigation_and_custom_description():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.radio[0].set_value("How it works").run()
    assert not app.exception and app.title[0].value == "Clarity behind every score."
    app.radio[0].set_value("Resume analyzer").run()
    next(b for b in app.button if b.label == "Try ML Engineer").click().run()
    assert app.selectbox[0].value == "Machine Learning Engineer"
    app.text_area[0].set_value("Required skills include Python, SQL, FastAPI and Docker for building APIs.")
    next(b for b in app.button if b.label == "Compare with job description").click().run()
    assert not app.exception and app.session_state["custom_role"].custom
