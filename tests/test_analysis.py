import random
from pathlib import Path

import pytest

from src.datasets import DatasetError, load_datasets
from src.job_description import JobDescriptionError, parse_job_description
from src.models import ParsedDocument
from src.pipeline import analyze_document
from src.resume_feedback import resume_feedback
from src.roadmap_generator import generate_roadmap
from src.section_detector import detect_sections
from src.skill_extractor import extract_skills
from src.text_cleaner import clean_text, comparison_text


def names(text, dictionary):
    return {e.name for e in extract_skills(detect_sections(text), dictionary)}


def test_technical_symbols_preserved(dictionary):
    text = "Skills:\n C++  C# .NET Node.js React.js Next.js CI/CD REST APIs scikit-learn\n=====\n"
    clean = clean_text(text)
    for term in ["C++", "C#", ".NET", "Node.js", "React.js", "Next.js", "CI/CD", "REST APIs", "scikit-learn"]:
        assert term in clean
    assert {"C++", "C#", ".NET", "Node.js", "React", "Next.js", "CI/CD", "REST APIs", "scikit-learn"} <= names(text, dictionary)
    assert comparison_text(" PYTHON  \r\n SQL ") == "python\nsql"


@pytest.mark.parametrize("text,expected", [("Skills: JS, Postgres, ML, PowerBI", {"JavaScript", "PostgreSQL", "Machine Learning", "Power BI"}), ("Skills: Python Python python", {"Python"}), ("Skills: Golang", {"Go"})])
def test_aliases_and_deduplication(text, expected, dictionary):
    assert names(text, dictionary) == expected


@pytest.mark.parametrize("text,absent", [("Skills: JavaScript", {"Java"}), ("Skills: C++ C#", {"C"}), ("Skills: R&D in marketing and forecasting", {"R", "C", "Go"}), ("I go to work every day", {"Go"}), ("Skills: React native. Email: python@example.com", {"Python"}), ("Skills: MySQL", {"SQL"}), ("Skills: currently learning Docker", {"Docker"}), ("Skills: No experience with Python", {"Python"})])
def test_false_positive_prevention(text, absent, dictionary):
    assert not names(text, dictionary) & absent


def test_deep_learning_does_not_suppress_following_skills(dictionary):
    assert {"Deep Learning", "PyTorch"} <= names("Skills: Deep Learning, PyTorch", dictionary)


def test_dictionary_canonical_terms_work(dictionary):
    for skill in dictionary.values():
        assert skill.name in names("Skills: " + skill.name, dictionary), skill.name


def test_sections_and_context(dictionary):
    sections = detect_sections("WORK EXPERIENCE\nBuilt APIs with Python.\nACADEMIC PROJECTS:\nCreated a SQL application.\nTECHNICAL SKILLS: Docker\nEducation\nBCA")
    assert set(sections) == {"Experience", "Projects", "Skills", "Education"}
    evidence = {s.name: s for s in extract_skills(sections, dictionary)}
    assert evidence["Python"].status == "Contextual mention"
    assert evidence["Docker"].status == "Mention only"


def test_fallback_without_sections():
    a = analyze_document(ParsedDocument("text.pdf", "I develop applications with Python and SQL and build tested data workflows.", 100, 1))
    assert {"Python", "SQL"} <= {s.name for s in a.skills}
    assert any("No standard" in n for n in a.notices)


def test_protected_fields_and_header_cannot_award_skills(dictionary, matcher):
    base = "Name: Sample Person\nSkills: Python, SQL\nProjects\nUsed Python to process data."
    changed = "Python R Docker\nGender: Python\nAge: 99\nSkills: Python, SQL\nProjects\nUsed Python to process data.\nPersonal Details\nReligion: Docker\nNationality: R\nDisability: FastAPI\nMarital status: Excel"
    assert names(base, dictionary) == names(changed, dictionary) == {"Python", "SQL"}
    assert matcher.rank(names(base, dictionary)) == matcher.rank(names(changed, dictionary))


@pytest.mark.parametrize("field", ["gender", "age", "religion", "nationality", "photograph", "marital status", "disability", "caste"])
def test_protected_attribute_counterfactual(field, dictionary, matcher):
    a = names(f"Skills: Python, SQL\n{field}: alpha", dictionary)
    b = names(f"Skills: Python, SQL\n{field}: beta", dictionary)
    assert matcher.rank(a) == matcher.rank(b)


def test_monotonic_scores_for_every_role(matcher, roles):
    randomizer = random.Random(41)
    for role in roles:
        for _ in range(12):
            order = list(role.required + role.preferred)
            randomizer.shuffle(order)
            detected = set()
            previous = 0.0
            for skill in order:
                detected.add(skill)
                score = matcher.match(detected, role).score
                assert previous <= score <= 100
                previous = score
            assert previous == 100.0
            detected.remove(order[-1])
            assert matcher.match(detected, role).score < 100.0


def test_irrelevant_skills_do_not_dilute_and_scores_are_repeatable(matcher, roles):
    first = matcher.match({"Python", "SQL"}, roles[0])
    assert first == matcher.match({"Python", "SQL"}, roles[0])
    assert first.score == matcher.match({"Python", "SQL", "Rust", "C++"}, roles[0]).score
    assert matcher.match({"Python", "SQL", "Pandas", "Power BI"}, roles[0]).score > first.score
    assert all(m.score == 0 for m in matcher.rank(set()))


def test_gap_sets_and_roadmap_dependencies(matcher, roles, dictionary):
    role = next(r for r in roles if r.name == "Machine Learning Engineer")
    detected = {"Python", "Machine Learning", "scikit-learn"}
    match = matcher.match(detected, role)
    assert set(match.missing) == {"FastAPI", "Docker"}
    plan = generate_roadmap(match, detected, dictionary)
    sequence = [p.skill for p in plan]
    assert sequence.index("REST APIs") < sequence.index("FastAPI")
    assert sequence.index("Linux") < sequence.index("Docker")
    assert not set(sequence) & detected
    assert sequence[-1] == "Applied project"


def test_complete_profile_gets_application_plan(matcher, roles, dictionary):
    role = roles[0]
    detected = set(role.required + role.preferred)
    plan = generate_roadmap(matcher.match(detected, role), detected, dictionary)
    assert len(plan) == 1 and plan[0].skill == "Applied project"


def test_custom_jd(dictionary, matcher):
    role, notes = parse_job_description("Required skills:\nPython, SQL, Docker.\nPreferred skills:\nFastAPI and Redis.", dictionary)
    assert set(role.required) == {"Python", "SQL", "Docker"}
    assert set(role.preferred) == {"FastAPI", "Redis"}
    assert notes and 0 < matcher.match({"Python", "SQL"}, role).score < 100


@pytest.mark.parametrize("text", ["", "No supported technologies here, just enthusiasm and motivation.", "x" * 30001])
def test_custom_jd_errors(text, dictionary):
    with pytest.raises(JobDescriptionError):
        parse_job_description(text, dictionary)


def test_empty_preferred_redistributes_weight(dictionary, matcher):
    role, _ = parse_job_description("Required skills for this role include Python and SQL.", dictionary)
    match = matcher.match({"Python", "SQL"}, role)
    assert match.required_points == 90 and match.preferred_points == 0 and match.score == 100


def test_feedback_grounded_in_missing_sections(matcher, roles):
    feedback = resume_feedback({}, "A hard-working developer", matcher.match({"Python"}, roles[0]))
    assert any("Skills heading" in f.detail for f in feedback)
    assert any("do not invent" in f.detail.lower() or "truthful" in f.detail.lower() for f in feedback)


def test_missing_dataset_has_safe_error(tmp_path):
    with pytest.raises(DatasetError, match="data folder") as exc:
        load_datasets(Path(tmp_path))
    assert str(tmp_path) not in str(exc.value)
