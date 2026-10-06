"""Boundary-aware alias matching; evidence describes text, never ability."""
import re
from functools import lru_cache

from src.models import Skill, SkillEvidence
from src.section_detector import job_content

# Compact single-letter names are deliberately case sensitive. Go uses Golang /
# explicit programming context; casual 'go' should never award a technical skill.
SHORT_CASE_SENSITIVE = {"R", "C", "ML", "AI", "CV"}
NEGATION = re.compile(r"(?:\b(?:no experience with|no experience in|without|lack(?:ing)?|never used|not familiar with|unfamiliar with|currently learning|plan to learn|want to learn)\b)[^.;\n]{0,42}$", re.I)


@lru_cache(maxsize=512)
def _pattern(alias: str) -> re.Pattern:
    escaped = re.escape(alias).replace(r"\ ", r"[ \t]+")
    # A period at the end of a sentence is allowed. Prefix punctuation prevents
    # Java matching inside a URL or R inside an abbreviation such as R&D.
    before = r"(?<![\w+#./&-])"
    after = r"(?![\w+#/-])"
    if alias == "R":
        after = r"(?![\w+#/&-])"
    return re.compile(before + escaped + after, 0 if alias in SHORT_CASE_SENSITIVE else re.I)


def extract_skills(sections: dict[str, str], dictionary: dict[str, Skill], *, job_description: bool = False) -> list[SkillEvidence]:
    content = job_content(sections)
    found = []
    for skill in dictionary.values():
        locations: dict[tuple[str, int, int], str] = {}
        for section, text in content.items():
            for alias in dict.fromkeys((skill.name, *skill.aliases)):
                for match in _pattern(alias).finditer(text):
                    line_start = text.rfind("\n", 0, match.start()) + 1
                    prefix = text[max(line_start, match.start() - 60):match.start()]
                    if not job_description and NEGATION.search(prefix):
                        continue
                    if alias == "Go" and not (section == "Skills" or re.search(r"\b(?:programming|golang|language|backend)\b", text[max(0, match.start()-35):match.end()+35], re.I)):
                        continue
                    locations[(section, match.start(), match.end())] = section
        if locations:
            # Overlapping aliases count once (e.g. 'ML' within 'ML engineering').
            unique = []
            for location in sorted(locations):
                if not any(location[0] == p[0] and location[1] >= p[1] and location[2] <= p[2] for p in unique):
                    unique.append(location)
            names = tuple(sorted({loc[0] for loc in unique}))
            contextual = bool(set(names) & {"Projects", "Experience", "Internships"})
            found.append(SkillEvidence(skill.name, skill.category, len(unique), names, "Contextual mention" if contextual else "Mention only"))
    return sorted(found, key=lambda evidence: (evidence.category, evidence.name.casefold()))
