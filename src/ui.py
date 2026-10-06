"""Presentation helpers keep escaped markup separate from the analysis logic."""
from html import escape

import streamlit as st

from src.config import ROOT


def apply_theme():
    st.html("<style>" + (ROOT / "assets" / "style.css").read_text(encoding="utf-8") + "</style>")


def chips(names, *, missing=False):
    if not names:
        st.caption("None")
        return
    variant = "chip-gap" if missing else "chip"
    st.html('<div class="chips">' + "".join(f'<span class="{variant}">{escape(name)}</span>' for name in names) + "</div>")


def intro():
    st.html('''<div class="hero"><div class="eyebrow">YOUR NEXT CHAPTER, WITH CLARITY</div><h1>Turn your resume<br>into a direction.</h1><p>See where your skills fit. Understand the gaps.<br>Build a practical plan for what comes next.</p><div class="hero-tags"><span>Private by design</span><span>Explainable scores</span><span>No API key needed</span></div><div class="hero-orbit" aria-hidden="true"><div></div></div></div>''')


def role_card(rank, match):
    st.html(f'''<div class="role-card"><div class="eyebrow">MATCH {rank:02d} / {escape(match.role.category)}</div><h3>{escape(match.role.name)}</h3><div class="role-score">{match.score:.1f}<span>%</span></div><p>{len(match.matched)} of {len(match.role.required)} core skills detected</p></div>''')


def methodology():
    st.title("Clarity behind every score.")
    st.write("CareerLens compares documented technical skills with curated educational role profiles. Every point can be traced to detected skills.")
    st.subheader("The scoring formula")
    st.latex(r"\text{Score} = 75R + 15P + 10C")
    st.markdown("**R** = core skills detected ÷ core skills expected. **P** = preferred skills detected ÷ preferred skills expected. **C** = TF-IDF cosine similarity between the role's skills and the resume's role-relevant skills. Each term is in [0, 1]. If a target has no preferred skills, the formula is **90R + 10C**.")
    st.info("This is a documented-skill alignment score. It is not an ATS certification, a recruiter decision, or the probability of being hired.")
    with st.expander("Why adding relevant skills cannot lower your score", expanded=True):
        st.write("We encode canonical skills as binary tokens and fit IDF once on the 13 role profiles. For each role, the resume vector contains only detected skills required or preferred by that role. Its weighted components match the role vector, so cosine similarity is the square root of the fraction of the role's squared IDF weight that is present. Adding a target skill increases or preserves every component; repeating a skill adds nothing.")
        st.write("This deliberately measures lexical skill overlap. We do not send full resume text to an embedding model or language model, and do not claim semantic understanding.")
    with st.expander("Evidence, fairness and limitations", expanded=True):
        st.markdown("- **Contextual mention:** a skill occurs under Projects, Experience or Internships.\n- **Mention only:** the term is found elsewhere; proficiency is unknown.\n- Education and certificates are shown for context but receive no score weight.\n- Gender, age, religion, nationality, photographs, marital status and disability are not scoring features. Recognized personal fields/sections are excluded.\n- A missing keyword does not prove a missing ability.\n- Templates describe common technical profiles; they are not live vacancies or universal employer requirements.\n- Scanned PDFs need OCR. Complex columns, text boxes, unusual headings, ambiguous terms and nuanced negation can reduce extraction quality. English technical resumes are the supported scope.")
    st.subheader("Your documents stay under your control")
    st.write("Uploads and analysis are held in this session's memory. The app has no accounts, database, external AI calls, or resume-content logs. Clear session removes the app's references and resets upload widgets. Disconnect cleanup is managed by Streamlit; hosted infrastructure may maintain routine request logs. Downloaded reports remain on your device.")
    st.caption("Made for learning and career guidance. Never use it for automatic hiring or rejection.")
