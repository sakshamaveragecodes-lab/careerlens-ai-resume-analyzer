"""Build a transparent custom target from recognized JD skills."""
import re

from src.models import Role, Skill
from src.skill_extractor import extract_skills
from src.text_cleaner import clean_text


class JobDescriptionError(ValueError):
    """User-correctable description error."""


def parse_job_description(text: str, skills: dict[str, Skill]) -> tuple[Role, list[str]]:
    if len(text) > 30_000:
        raise JobDescriptionError("Use a job description of at most 30,000 characters.")
    text = clean_text(text)
    if len(text) < 30:
        raise JobDescriptionError("Paste a fuller job description, including the required skills.")
    required: set[str] = set()
    preferred: set[str] = set()
    mode = "required"
    for line in text.splitlines():
        if re.search(r"^(?:nice[ -]to[ -]have|preferred|desirable|bonus|optional)\b", line, re.I):
            mode = "preferred"
        elif re.search(r"^(?:required|requirements|must[ -]have|essential|minimum|responsibilities|qualifications)\b", line, re.I):
            mode = "required"
        hits = {s.name for s in extract_skills({"Skills": line}, skills, job_description=True)}
        if re.search(r"\b(?:not required|no experience (?:with|in))\b", line, re.I):
            continue
        destination = preferred if mode == "preferred" or re.search(r"\b(?:preferred|nice to have|bonus)\b", line, re.I) else required
        destination.update(hits)
    preferred -= required
    notes = ["Only recognized technical skills affect this score. Review the extracted requirements; pay, location, eligibility, degrees and years of experience are not scored."]
    if not required and preferred:
        required, preferred = preferred, set()
        notes.append("Only optional skills were found; they are used as the comparison set. Check this interpretation before relying on the result.")
    if not required:
        raise JobDescriptionError("No supported technical requirements were detected. Add explicit skills (for example Python, SQL, Docker) or use a predefined role.")
    role = Role("Custom job description", "Custom target", "Requirements extracted from the job description you provided.", tuple(sorted(required)), tuple(sorted(preferred)), "Build a small project that demonstrates the key requirements in this job description. Document setup, tests, results, and a reproducible example.", True)
    return role, notes
