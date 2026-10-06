"""Reproduce a small, explicitly synthetic evaluation set (not a benchmark)."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets import load_datasets  # noqa: E402
from src.models import ParsedDocument  # noqa: E402
from src.pipeline import analyze_document  # noqa: E402
from src.resume_parser import parse_document  # noqa: E402

PROFILE_LABELS = {
    "data_analyst": ("Data Analyst", {"Python", "SQL", "Excel", "Pandas", "Power BI", "Statistics", "Data Visualization", "Data Cleaning"}),
    "ml_engineer": ("Machine Learning Engineer", {"Python", "Machine Learning", "scikit-learn", "FastAPI", "Docker", "Pandas", "SQL", "Model Evaluation", "Git", "Unit Testing", "APIs"}),
    "nlp_engineer": ("NLP Engineer", {"Python", "NLP", "Transformers", "Hugging Face", "spaCy", "Text Classification", "Named Entity Recognition", "PyTorch", "Model Evaluation"}),
}


def main():
    rows = []
    total_tp = total_fp = total_fn = 0
    for stem, (expected_role, expected_skills) in PROFILE_LABELS.items():
        for extension in ("pdf", "docx"):
            path = ROOT / "sample_resumes" / f"{stem}.{extension}"
            document = parse_document(path.name, path.read_bytes())
            analysis = analyze_document(document)
            actual = {s.name for s in analysis.skills}
            tp = len(actual & expected_skills)
            fp = len(actual - expected_skills)
            fn = len(expected_skills - actual)
            total_tp += tp
            total_fp += fp
            total_fn += fn
            reference = (ROOT / "sample_resumes" / f"{stem}.txt").read_text(encoding="utf-8")
            extraction = " ".join(document.text.split()) == " ".join(reference.split())
            rows.append({"Test resume": path.name, "Expected top role": expected_role, "Actual top role": analysis.rankings[0].role.name, "Top score": analysis.rankings[0].score, "Skill precision": round(tp / (tp + fp), 4) if tp + fp else 0, "Skill recall": round(tp / (tp + fn), 4), "Extraction text equivalent": extraction, "Result": "PASS" if expected_role == analysis.rankings[0].role.name and not fp and not fn and extraction else "REVIEW", "Comments": "Synthetic labelled fixture; no claim of real-world accuracy."})
    # Counterfactual pair plus a meaningful incomplete-profile comparison.
    probes = [
        ("Sparse skills", "Skills: Python, SQL\nEducation: Bachelor of Computer Applications", None),
        ("Enriched skills", "Skills: Python, SQL, Pandas, Power BI\nEducation: Bachelor of Computer Applications", "Data Analyst"),
        ("Protected fields variant A", "Skills: Python, SQL, Pandas, Power BI\nGender: female\nAge: 25\nNationality: Indian", "Data Analyst"),
        ("Protected fields variant B", "Skills: Python, SQL, Pandas, Power BI\nGender: male\nAge: 52\nNationality: Canadian\nDisability: disclosed", "Data Analyst"),
    ]
    for name, text, expected in probes:
        analysis = analyze_document(ParsedDocument(name, text, len(text), None))
        rows.append({"Test resume": name, "Expected top role": expected or "Exploratory - no top-1 assertion", "Actual top role": analysis.rankings[0].role.name, "Top score": analysis.rankings[0].score, "Skill precision": "", "Skill recall": "", "Extraction text equivalent": "N/A - direct text", "Result": "PASS" if not expected or analysis.rankings[0].role.name == expected else "REVIEW", "Comments": "Deterministic text probe; not a labelled hiring outcome."})
    output = ROOT / "reports"
    output.mkdir(exist_ok=True)
    with (output / "evaluation.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {"evaluated_files": 6, "labelled_profiles": 3, "top_1_correct": sum(row["Expected top role"] == row["Actual top role"] for row in rows[:6]), "micro_precision": total_tp / (total_tp + total_fp), "micro_recall": total_tp / (total_tp + total_fn), "text_equivalence_passes": sum(row["Extraction text equivalent"] is True for row in rows[:6]), "dictionary_skills": len(load_datasets()[0]), "roles": len(load_datasets()[1]), "limitations": "Three authored synthetic profiles, each exported to two formats. Labels were manually specified. This is a smoke evaluation, not independent real-world validation."}
    (output / "evaluation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if any(row["Result"] != "PASS" for row in rows):
        raise SystemExit("Evaluation contains cases requiring review; inspect reports/evaluation.csv.")


if __name__ == "__main__":
    main()
