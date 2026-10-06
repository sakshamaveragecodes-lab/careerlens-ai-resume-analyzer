"""Generate a structured PDF in memory, escaping all user-derived strings."""
import io
from collections import Counter
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

from src.config import DISCLAIMER
from src.models import Analysis, Feedback, Match, RoadmapStep
from src.pdf_fonts import register_fonts

NAVY = colors.HexColor("#142D36")
TEAL = colors.HexColor("#007968")


def _safe(text: object) -> str:
    # Keep arbitrary filenames inside the report's supported character set.
    value = str(text).replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    return escape(value.encode("cp1252", "replace").decode("cp1252")).replace("\n", "<br/>")


def generate_report(analysis: Analysis, target: Match, roadmap: list[RoadmapStep], feedback: list[Feedback]) -> bytes:
    register_fonts()
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", fontName="CareerSans-Bold", fontSize=25, leading=30, textColor=NAVY, spaceAfter=10))
    styles.add(ParagraphStyle(name="Eyebrow", fontName="CareerSans-Bold", fontSize=9, leading=13, textColor=TEAL, spaceAfter=10))
    styles.add(ParagraphStyle(name="Copy", fontName="CareerSans", fontSize=9.5, leading=14, textColor=NAVY, spaceAfter=7, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="Section", fontName="CareerSans-Bold", fontSize=14, leading=18, textColor=NAVY, spaceBefore=15, spaceAfter=8, keepWithNext=True))
    doc = SimpleDocTemplate(buffer, pagesize=(595.28, 841.89), rightMargin=44, leftMargin=44, topMargin=44, bottomMargin=48, title="CareerLens Resume Analysis", author="CareerLens")
    def p(value, style="Copy"):
        return Paragraph(_safe(value), styles[style])
    story = [p("CAREERLENS / CAREER INTELLIGENCE", "Eyebrow"), p("Your resume.\nYour next step.", "ReportTitle"), p(f"Analysis date (UTC): {analysis.analyzed_at}"), p(f"Document: {analysis.document.filename}"), p(f"Target: {target.role.name}"), Spacer(1, 8)]
    metrics = [[p(f"{target.score:.1f}%\nSkill alignment"), p(f"{len(analysis.skills)}\nSkills detected"), p(f"{len(target.missing)}\nCore skills not detected")]]
    table = Table(metrics, colWidths=[169, 169, 169])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF4F0")), ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 9), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [table, Spacer(1, 12), p(DISCLAIMER)]
    for notice in analysis.notices:
        story.append(p(notice))
    story += [p("Recommended roles", "Section")]
    for i, result in enumerate(analysis.rankings[:3], 1):
        story.append(p(f"{i}. {result.role.name} - {result.score:.1f}% ({len(result.matched)}/{len(result.role.required)} core skills detected)"))
    story += [p("Target-role skill gaps", "Section"), p("Core detected: " + (", ".join(target.matched) or "None")), p("Core not detected in the resume: " + (", ".join(target.missing) or "None")), p("Preferred detected: " + (", ".join(target.preferred_matched) or "None")), p("Preferred not detected: " + (", ".join(target.preferred_missing) or "None"))]
    story += [p("All detected skills", "Section")]
    for category in sorted(Counter(s.category for s in analysis.skills)):
        story.append(p(category + ": " + ", ".join(s.name for s in analysis.skills if s.category == category)))
    contextual = [s.name for s in analysis.skills if s.status == "Contextual mention"]
    mentions = [s.name for s in analysis.skills if s.status == "Mention only"]
    story += [p("Evidence strength", "Section"), p("Project/work-section mentions: " + (", ".join(contextual) or "None")), p("Mention only; add evidence where truthful: " + (", ".join(mentions) or "None")), p("These labels describe where terms appear, not independently verified skill levels. Repetition does not increase the score.")]
    story += [p("Personalized learning plan", "Section"), p("Each week is a suggested study block of roughly 5-8 hours. Adjust the pace to your background. Dependencies may add foundation topics; this is not a promise of mastery.")]
    for step in roadmap:
        chunk = [p(f"Week {step.week}: {step.skill}", "Eyebrow"), p(step.purpose + ". " + step.topic), p("Practice: " + step.exercise)]
        if step.resource:
            chunk.append(Paragraph(f'<link href="{escape(step.resource, {chr(34): "&quot;"})}" color="#007968">Official learning resource</link>', styles["Copy"]))
        story.append(KeepTogether(chunk + [Spacer(1, 6)]))
    for index, item in enumerate(feedback):
        heading = [p("Resume improvements", "Section")] if index == 0 else []
        story.append(KeepTogether(heading + [p(item.title, "Eyebrow"), p(item.detail)]))
    story += [p("How your score is calculated", "Section"), p("With preferred skills: 75 x core coverage + 15 x preferred coverage + 10 x TF-IDF cosine similarity. Without preferred skills: 90 x core coverage + 10 x similarity. Coverage and similarity are fractions from 0 to 1."), p(f"Core: {target.required_points:.2f} points; preferred: {target.preferred_points:.2f} points; similarity: {target.similarity_points:.2f} points. Total rounded to one decimal: {target.score:.1f}."), p("Both TF-IDF vectors contain canonical, role-relevant skill tokens only. The resume vector is projected onto the target's skills. The fixed vocabulary and IDF values are learned from the 13 curated role profiles, not from personal resume text. This is lexical skill similarity, not semantic understanding."), p("Gender, age, religion, nationality, photographs, marital status and disability are not score features. Recognized personal fields and sections are excluded from skill extraction. Education and section context inform the displayed analysis but do not change the score. The dictionary and role templates are educational, not employer-validated hiring criteria."), p("Privacy", "Section"), p("This report contains derived analysis only, not the full resume text. Uploaded bytes and results are held in the active session's memory and are not written to an application database. Use Clear session to discard them. Your browser download is your own copy.")]

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#DCE6E1"))
        canvas.line(44, 36, 551, 36)
        canvas.setFont("CareerSans", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(44, 24, "CAREERLENS | Educational career guidance")
        canvas.drawRightString(551, 24, f"{document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
