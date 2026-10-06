"""Tolerant heading detection and a conservative job-content projection."""
import re

ALIASES = {
    "Summary": ("summary", "profile", "professional summary", "professional profile", "objective", "career objective", "about me"),
    "Skills": ("skills", "technical skills", "core skills", "technical expertise", "core competencies", "technologies", "skills and tools", "key skills"),
    "Education": ("education", "academic qualifications", "educational qualifications", "academic background"),
    "Experience": ("experience", "work experience", "professional experience", "employment", "employment history", "work history"),
    "Internships": ("internships", "internship", "internship experience"),
    "Projects": ("projects", "academic projects", "personal projects", "selected projects", "technical projects", "project experience"),
    "Certifications": ("certifications", "certificates", "courses", "licenses and certifications", "training"),
    "Achievements": ("achievements", "awards", "honors", "accomplishments"),
    "Personal": ("personal details", "personal information", "contact", "contact information", "references", "declaration"),
}
HEADING_MAP = {alias: section for section, aliases in ALIASES.items() for alias in aliases}
PERSONAL_LABEL = re.compile(
    r"^\s*(?:[-•*]\s*)?(?:full name|name|gender|sex|age|d\.?o\.?b\.?|date of birth|"
    r"religion|nationality|citizenship|marital status|disability|disabilities|caste|ethnicity|race|"
    r"photograph|photo|pronouns|address|phone|mobile|email|e-mail|passport)\s*[:=|\-]", re.I
)


def detect_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"Unsectioned": []}
    current = "Unsectioned"
    for line in text.splitlines():
        stripped = re.sub(r"^\s*[#•*\d.)-]+\s*", "", line).strip()
        key, separator, content = stripped.partition(":")
        heading = HEADING_MAP.get(key.strip().lower().rstrip(" -|"))
        if heading and (separator or len(stripped) < 60):
            current = heading
            sections.setdefault(current, [])
            if separator and content.strip():
                sections[current].append(content.strip())
        else:
            sections.setdefault(current, []).append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items() if "\n".join(lines).strip() or name != "Unsectioned"}


def job_content(sections: dict[str, str]) -> dict[str, str]:
    result = {}
    has_structure = any(name not in {"Personal", "Unsectioned"} for name in sections)
    for name, content in sections.items():
        if name == "Personal" or (name == "Unsectioned" and has_structure):
            continue
        lines = []
        for line in content.splitlines():
            if PERSONAL_LABEL.search(line):
                continue
            # Remove URLs / email addresses so e.g. react@example.com is not a skill.
            line = re.sub(r"\b\S+@\S+\b|https?://\S+|www\.\S+", " ", line)
            lines.append(line)
        result[name] = "\n".join(lines)
    return result
