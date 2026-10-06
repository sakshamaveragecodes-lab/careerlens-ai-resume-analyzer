"""Streamlit entrypoint. Start with: python -m streamlit run app.py"""
import streamlit as st

from src.charts import category_chart, coverage_chart, ranking_chart
from src.config import DISCLAIMER, MAX_UPLOAD_MB, ROOT
from src.datasets import DatasetError, load_datasets
from src.job_description import JobDescriptionError, parse_job_description
from src.job_matcher import JobMatcher
from src.pipeline import analyze_document
from src.report_generator import generate_report
from src.resume_feedback import resume_feedback
from src.resume_parser import DocumentError, parse_document
from src.roadmap_generator import generate_roadmap
from src.ui import apply_theme, chips, intro, methodology, role_card

st.set_page_config(page_title="CareerLens - AI Resume Analyzer", page_icon="◉", layout="wide", initial_sidebar_state="expanded")
apply_theme()


@st.cache_resource
def resources():
    dictionary, role_data = load_datasets()
    return dictionary, role_data, JobMatcher(role_data, list(dictionary))


def clear_analysis():
    for key in ("analysis", "report", "report_key", "custom_role", "custom_notes", "sample_name"):
        st.session_state.pop(key, None)


def clear_session():
    upload_generation = st.session_state.get("upload_generation", 0) + 1
    for key in list(st.session_state):
        del st.session_state[key]
    # File uploaders retain browser-side state unless their widget identity changes.
    st.session_state.upload_generation = upload_generation


def analyze_bytes(name, data):
    clear_analysis()
    try:
        with st.status("Reading your document...", expanded=False) as status:
            document = parse_document(name, data)
            status.update(label="Mapping skills and comparing roles...")
            result = analyze_document(document, matcher)
            st.session_state.analysis = result
            status.update(label="Analysis ready", state="complete")
    except DocumentError as exc:
        st.error(str(exc))


def load_sample(filename, target, label):
    st.session_state.target_role = target
    analyze_bytes(filename, (ROOT / "sample_resumes" / filename).read_bytes())
    st.session_state.sample_name = label


try:
    dictionary, roles, matcher = resources()
except DatasetError as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    st.markdown("# CareerLens")
    st.caption("A clearer view of your next move.")
    st.divider()
    page = st.radio("Workspace", ["Resume analyzer", "How it works"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Built for your next chapter**")
    st.caption(f"{len(roles)} career profiles · {len(dictionary)} recognized skills")
    st.caption("PDF + DOCX · No paid API")
    st.markdown("**Private by design**")
    st.caption("Documents stay in session memory. No account, database or external AI service.")
    st.button("Clear session", on_click=clear_session, width="stretch", help="Discard this session's uploads, analysis and report.")
    st.caption("Educational career guidance.\nNever a hiring decision.")

if page == "How it works":
    methodology()
    st.stop()

intro()
st.subheader("01 / Start with your story")
left, right = st.columns([1.25, 1], gap="large")
with left:
    upload = st.file_uploader("Upload your resume", type=["pdf", "docx"], max_upload_size=MAX_UPLOAD_MB, key=f"resume_upload_{st.session_state.get('upload_generation', 0)}", on_change=clear_analysis, help=f"Text-based PDF or DOCX, up to {MAX_UPLOAD_MB} MB and 20 PDF pages.")
    if upload is not None:
        st.caption(f"{upload.name} · {upload.size / 1024:.1f} KB · {upload.name.rsplit('.', 1)[-1].upper()}")
    st.caption(f"Up to {MAX_UPLOAD_MB} MB. Scanned PDFs need OCR before upload. Use the × next to the file to remove or replace it.")
    if st.button("Analyze resume", type="primary", disabled=upload is None, width="stretch"):
        analyze_bytes(upload.name, upload.getvalue())
with right:
    target_name = st.selectbox("Target job role", [r.name for r in roles], key="target_role")
    selected_role = next(r for r in roles if r.name == target_name)
    st.write(selected_role.description)
    st.caption("Change your target at any time. The same resume is compared with all 13 roles.")
    st.info("Only documented job skills affect the score. Personal characteristics do not.", icon="ℹ️")

with st.expander("Just exploring? Try a synthetic resume", expanded="analysis" not in st.session_state):
    st.caption("Fictional profiles included for testing. No real personal information.")
    for col, label, filename, target in zip(st.columns(3), ["Data Analyst", "ML Engineer", "NLP Engineer"], ["data_analyst.pdf", "ml_engineer.docx", "nlp_engineer.pdf"], [r.name for r in (roles[0], roles[1], roles[3])]):
        with col:
            st.button("Try " + label, width="stretch", on_click=load_sample, args=(filename, target, label))

if "analysis" not in st.session_state:
    st.divider()
    st.subheader("From upload to a practical next step.")
    for col, title, copy in zip(st.columns(3), ["01  Understand", "02  Compare", "03  Grow"], ["See the skills and sections found in your resume.", "Explore role matches with a transparent score breakdown.", "Turn missing skills into an ordered plan with practice projects."]):
        with col:
            st.markdown("**" + title + "**")
            st.caption(copy)
    st.stop()

analysis = st.session_state.analysis
detected = {s.name for s in analysis.skills}
target = matcher.match(detected, selected_role)
st.divider()
st.subheader("02 / See where you stand")
st.caption("Analyzing " + analysis.document.filename + " · " + ("Synthetic example" if st.session_state.get("sample_name") else "Your uploaded resume"))
for notice in analysis.notices:
    st.warning(notice)
cols = st.columns(4)
cols[0].metric("Target skill alignment", f"{target.score:.1f}%", help="Documented skill match; not a hiring probability.")
cols[1].metric("Skills detected", len(analysis.skills))
cols[2].metric("Core skills not detected", len(target.missing))
cols[3].metric("Roles compared", len(analysis.rankings))
st.caption(DISCLAIMER)

overview, skills_tab, roadmap_tab, insights_tab, jd_tab, report_tab = st.tabs(["Overview", "Skills & gaps", "Learning plan", "Resume insights", "Custom job", "Report"])
with overview:
    st.subheader("Your strongest role matches")
    for i, (col, match) in enumerate(zip(st.columns(3), analysis.rankings[:3]), 1):
        with col:
            role_card(i, match)
    col1, col2 = st.columns([1.8, 1], gap="large")
    with col1:
        st.markdown("#### All role matches")
        st.plotly_chart(ranking_chart(analysis.rankings, target_name), width="stretch", config={"displayModeBar": False})
    with col2:
        st.markdown("#### Target core coverage")
        st.caption(target_name)
        st.plotly_chart(coverage_chart(target), width="stretch", config={"displayModeBar": False})
        st.caption(f"{len(target.matched)} core skills detected; {len(target.missing)} not detected.")
        st.markdown("**Score breakdown**")
        st.write(f"Core coverage: **{target.required_points:.2f} / 75**")
        st.write(f"Preferred coverage: **{target.preferred_points:.2f} / 15**")
        st.write(f"TF-IDF similarity: **{target.similarity_points:.2f} / 10**")
        st.caption("See How it works for the complete formula.")

with skills_tab:
    st.subheader("A clear view of the gaps")
    st.caption(target_name + " · Core skills")
    a, b = st.columns(2)
    with a:
        st.markdown("**Detected in your resume**")
        chips(target.matched)
    with b:
        st.markdown("**Not detected in your resume**")
        chips(target.missing, missing=True)
    with st.expander("Preferred skills"):
        st.write("Detected")
        chips(target.preferred_matched)
        st.write("Not detected")
        chips(target.preferred_missing, missing=True)
    st.info("Mention only means there is limited resume context, not that your ability is weak. Add a truthful project or work example where you have one.")
    if analysis.skills:
        st.dataframe([{"Skill": s.name, "Category": s.category, "Evidence": s.status, "Sections": ", ".join(s.sections), "Mentions": s.mentions} for s in analysis.skills], hide_index=True, width="stretch")
        st.plotly_chart(category_chart(analysis.skills), width="stretch", config={"displayModeBar": False})

with roadmap_tab:
    st.subheader("Make the next step a small one.")
    st.caption(f"Your plan for {target_name}. Suggested weeks are flexible study blocks of 5-8 hours, not a promise of mastery.")
    include_preferred = st.toggle("Include preferred skills in my plan", key="include_preferred")
    roadmap = generate_roadmap(target, detected, dictionary, include_preferred)
    if not target.missing:
        st.success("All core skill terms are present. Focus on evidence and applied practice; keyword coverage does not establish expertise.")
    for step in roadmap:
        with st.expander(f"Week {step.week:02d} · {step.skill}", expanded=step.week <= 2):
            st.caption(step.purpose)
            st.write(step.topic)
            st.markdown("**Practice:** " + step.exercise)
            if step.resource:
                st.link_button("Open official learning resource", step.resource)

feedback = resume_feedback(analysis.sections, analysis.cleaned_text, target)
with insights_tab:
    st.subheader("Tell the story behind your skills.")
    for item in feedback:
        with st.container(border=True):
            st.markdown("**" + item.title + "**")
            st.write(item.detail)
    st.markdown("#### Detected sections")
    for name, content in analysis.sections.items():
        if name == "Personal":
            continue
        with st.expander(f"{name} · {len(content.split())} words"):
            st.text(content or "Heading found, but no text detected beneath it.")
    with st.expander("Review original extracted text"):
        st.caption("This can include personal details. It stays in this session and is not included in the downloaded analysis report.")
        st.text(analysis.document.text)

with jd_tab:
    st.subheader("Have a specific opportunity in mind?")
    st.write("Paste a job description or upload it. Explicit Required and Preferred headings give the clearest result.")
    jd_text = st.text_area("Job description", height=180, max_chars=30_000, key="jd_text")
    jd_upload = st.file_uploader("Or upload a job description", type=["pdf", "docx", "txt"], max_upload_size=MAX_UPLOAD_MB, key="jd_upload")
    st.caption("If you provide both, the uploaded document takes precedence. Only recognized technical skills are compared; requirements such as location or work authorization need your own review.")
    if st.button("Compare with job description", type="primary"):
        st.session_state.pop("custom_role", None)
        try:
            content = parse_document(jd_upload.name, jd_upload.getvalue(), allow_txt=True).text if jd_upload is not None else jd_text
            custom_role, notes = parse_job_description(content, dictionary)
            st.session_state.custom_role = custom_role
            st.session_state.custom_notes = notes
        except (DocumentError, JobDescriptionError) as exc:
            st.error(str(exc))
    if "custom_role" in st.session_state:
        custom_match = matcher.match(detected, st.session_state.custom_role)
        st.metric("Custom job skill alignment", f"{custom_match.score:.1f}%")
        for note in st.session_state.custom_notes:
            st.caption(note)
        st.caption("Results use your last submitted job description. After editing it, click Compare again.")
        st.write("**Core requirements detected**")
        chips(custom_match.matched)
        st.write("**Core requirements not detected in your resume**")
        chips(custom_match.missing, missing=True)
        st.write("**Preferred requirements**")
        chips(custom_match.preferred_matched)
        chips(custom_match.preferred_missing, missing=True)
        st.write(f"Score components: core {custom_match.required_points:.2f} + preferred {custom_match.preferred_points:.2f} + similarity {custom_match.similarity_points:.2f} = **{custom_match.score:.1f}%** (rounded).")
        for item in resume_feedback(analysis.sections, analysis.cleaned_text, custom_match):
            st.markdown("**" + item.title + "** — " + item.detail)
        st.info("You can export this custom comparison from the Report tab.")

with report_tab:
    st.subheader("Take your next steps with you.")
    st.write("Your PDF includes the score, recommended roles, skill gaps, learning plan and resume feedback. It excludes the original resume text.")
    options = ["Selected target role"] + (["Custom job description"] if "custom_role" in st.session_state else [])
    report_choice = st.radio("Report target", options, horizontal=True)
    report_match = target if report_choice == "Selected target role" else matcher.match(detected, st.session_state.custom_role)
    report_key = (analysis.analyzed_at, analysis.document.filename, report_match.role, include_preferred)
    if st.session_state.get("report_key") != report_key:
        st.session_state.pop("report", None)
    if st.button("Prepare PDF report", type="primary"):
        try:
            with st.spinner("Preparing your report..."):
                plan = generate_roadmap(report_match, detected, dictionary, include_preferred)
                advice = resume_feedback(analysis.sections, analysis.cleaned_text, report_match)
                st.session_state.report = generate_report(analysis, report_match, plan, advice)
                st.session_state.report_key = report_key
        except Exception:
            st.error("The report could not be generated. Your analysis is still available. Try a shorter document or restart the session.")
    if "report" in st.session_state:
        st.download_button("Download analysis PDF", st.session_state.report, file_name="CareerLens_Analysis.pdf", mime="application/pdf", type="primary")
    st.caption("The PDF reflects your selected target and the preferred-skills toggle in Learning plan.")

st.divider()
st.caption("CAREERLENS · See the evidence. Choose your next step.")
