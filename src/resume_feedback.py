"""Conservative, testable writing feedback grounded in extracted sections."""
import re

from src.models import Feedback, Match


def resume_feedback(sections: dict[str, str], text: str, match: Match) -> list[Feedback]:
    items = []
    if not sections.get("Skills"):
        items.append(Feedback("Make your skills easy to find", "No clear Skills heading was detected. Add a concise skills section containing only technologies you can explain or demonstrate."))
    projects = sections.get("Projects", "")
    experience = "\n".join(sections.get(s, "") for s in ("Experience", "Internships"))
    if not projects:
        items.append(Feedback("Add evidence through a project", "No Projects section was detected. Describe a relevant project: the problem, your contribution, the technology, and the outcome."))
    elif len(projects.split()) < 35:
        items.append(Feedback("Give your project more context", "Your detected Projects section is brief. Explain what you built, the data or users involved, and how you checked the result."))
    if projects or experience:
        if not re.search(r"\b\d+(?:\.\d+)?\s*(?:%|percent|users|records|rows|seconds|hours|requests|datasets|ms|projects)\b|\d+(?:\.\d+)?%", projects + experience, re.I):
            items.append(Feedback("Use a measurable outcome when available", "No common outcome metric was found in the detected project/experience sections. Add truthful measures such as dataset size, accuracy with validation method, or time saved; do not invent numbers."))
    if not sections.get("Education"):
        items.append(Feedback("Use a clear Education heading", "Education was not found under a recognized heading. Include the qualification, subject, institution, and dates where relevant; education is shown for context and does not affect the score."))
    if not re.search(r"github\.com|gitlab\.com|portfolio|https?://", text, re.I):
        items.append(Feedback("Link to work you can demonstrate", "Consider a portfolio or repository link for a relevant project. Do not include confidential code or data."))
    if re.search(r"hard[ -]working|team player|go[ -]getter|results[ -]driven", text, re.I):
        items.append(Feedback("Replace generic claims with an example", "Generic wording was detected. A short example of a contribution is more informative than labels such as 'hard-working'."))
    if match.missing:
        items.append(Feedback("Check the target-role gaps", "Not detected: " + ", ".join(match.missing[:8]) + ". If you already use these skills, add truthful examples; otherwise follow the learning plan."))
    if not items:
        items.append(Feedback("Your core sections are present", "Review each bullet for a clear action, your contribution, and a verifiable result. Keyword presence alone cannot establish proficiency.", "positive"))
    return items
