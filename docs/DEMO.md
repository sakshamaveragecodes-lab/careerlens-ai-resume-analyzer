# Demonstration guide

Suggested duration: 3-4 minutes. Start the app and use the included fictional resumes. Explain actual behavior instead of claiming recruiter-level prediction accuracy.

| Time | Action | Explanation |
| --- | --- | --- |
| 0:00-0:25 | Show the home screen and privacy notice | The app analyzes documented skills without a paid API or persistent resume storage. |
| 0:25-0:55 | Upload `data_analyst.pdf`, select Data Analyst, Analyze | PDF text is extracted, cleaned and matched to a controlled dictionary. |
| 0:55-1:20 | Show Overview and role ranking | All 13 role profiles are compared; the top three are displayed. The score is alignment, not hiring probability. |
| 1:20-1:45 | Change target to Machine Learning Engineer; open Skills & gaps | The same resume can have different gaps for a different target. Missing means not detected. |
| 1:45-2:10 | Open Learning plan | Dependencies come first, already-detected skills are skipped and a relevant project closes the plan. |
| 2:10-2:30 | Open Resume insights | Section detection and constructive feedback are visible; the original text can be checked. |
| 2:30-2:55 | Paste `custom_job.txt` into Custom job and compare | Recognized required and preferred skills are displayed for review. |
| 2:55-3:15 | Prepare and download a PDF | The report contains results, roadmap and methodology, not the original resume text. |
| 3:15-3:35 | Replace with `ml_engineer.docx` and analyze | DOCX parsing supports paragraphs and tables. |
| 3:35-4:00 | Show How it works and Clear session | Explain the formula, privacy and limitations, then discard the session. |

The accompanying video uses actual browser interactions. It is a silent demonstration; use this table as a presentation script. Any checks that could not be performed are identified in `VERIFICATION.md`.
