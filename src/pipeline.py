"""Orchestrate analysis without caching or persisting user documents."""
from datetime import datetime, timezone

from src.datasets import load_datasets
from src.job_matcher import JobMatcher
from src.models import Analysis, ParsedDocument
from src.section_detector import detect_sections
from src.skill_extractor import extract_skills
from src.text_cleaner import clean_text


def analyze_document(document: ParsedDocument, matcher: JobMatcher | None = None) -> Analysis:
    skills, roles = load_datasets()
    matcher = matcher or JobMatcher(roles, list(skills))
    cleaned = clean_text(document.text)
    sections = detect_sections(cleaned)
    evidence = extract_skills(sections, skills)
    notices = list(document.warnings)
    if not any(name not in {"Unsectioned", "Personal"} for name in sections):
        notices.append("No standard section headings were detected. Skill matching used the readable non-personal text; section-based feedback may be incomplete.")
    if not evidence:
        notices.append("No dictionary skills were detected. Scores are zero and the alphabetical ranking does not indicate suitability. Check the extracted text or try a supported technical profile.")
    return Analysis(document, cleaned, sections, evidence, matcher.rank({s.name for s in evidence}), datetime.now(timezone.utc).isoformat(timespec="seconds"), notices)
