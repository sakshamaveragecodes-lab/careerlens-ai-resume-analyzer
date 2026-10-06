# Source import and cloud validation

Imported the application-root contents from the supplied project archive; outer delivery folders and ZIP/bundle files were not included. Application source, tests, project assets, documentation, sample data, model assets (when supplied), and dependency/configuration files were preserved. Ignore rules protect local secrets and generated development artifacts. Shell launchers are executable.

The existing verification documents and package manifests describe the supplied archive's historical run. The results below describe the cloud import validation on 2026-10-06.

Before publication, Gitleaks 8.24.2 scanned the publishable files and extracted text from PDF/DOCX deliverables with no credential findings. Blank `.env.example` templates are included; populated environment files and runtime credentials are excluded.

## Reproduce

Use Python 3.12.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt -r requirements-dev.txt
.venv/bin/ruff check .
.venv/bin/python -m pytest -q
.venv/bin/python scripts/evaluate.py
.venv/bin/python -m streamlit run app.py --server.headless=true
```

All 59 tests passed, including resume parsing, ranking, report generation and Streamlit sample/clear/custom-job journeys. Ruff passed. The supplied synthetic evaluation matched all six PDF/DOCX samples to their expected top role. Startup health and application HTML responded successfully. No API key or downloaded model is required. Docker execution was not tested.
