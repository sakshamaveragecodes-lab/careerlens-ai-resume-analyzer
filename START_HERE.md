# Start CareerLens

## Windows

Install Python 3.12 and extract the complete project folder. Double-click `start_windows.bat`.

Or open PowerShell in the extracted `careerlens` folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://localhost:8501. Keep the terminal open. No API key, account, database, model download or PowerShell activation is needed. Initial dependency installation needs internet access.

If port 8501 is in use, append `--server.port 8502` to the final command and open http://localhost:8502.

## First use

Select **Try Data Analyst**, or upload a readable PDF/DOCX and select **Analyze resume**. Explore the target-role score, gaps, learning plan and custom job comparison. The **Report** tab prepares a downloadable PDF. **Clear session** resets uploads and results.

## Included deliverables

- `README.md`: setup, usage, architecture, methodology, configuration and limitations.
- `docs/CareerLens_Project_Report.pdf`: four-page project report.
- `docs/demo/CareerLens_Demo.mp4`: 2 minute 54 second silent recording of actual browser interactions, slowed for readability.
- `docs/architecture.svg` and `.mmd`: architecture diagram and editable source.
- `docs/VIVA.md`: project-specific viva preparation.
- `docs/VERIFICATION.md`: executed checks and honest verification limits.
- `reports/evaluation.csv`: six synthetic files and four direct-text probes.
- `reports/Example_Analysis.pdf`: example generated analysis.
- `sample_resumes/`: three fictional resumes in PDF, DOCX and TXT, plus a custom job description.
- Source, datasets, tests, pinned dependencies, launchers and deployment configuration.

The application and local package are complete. GitHub publication and hosted deployment remain pending public-repository approval. Docker execution is unverified. The six sample files are a small synthetic evaluation, not proof of real-world accuracy.

For macOS/Linux commands, deployment and troubleshooting, see `README.md` and `docs/DEPLOYMENT.md`.
