# Verification record

## Executed checks

| Check | Evidence and outcome |
| --- | --- |
| Original automated suite | 59 tests passed in the preceding build session. Covers parsing, extraction, scoring, protected-field probes, roadmaps, JD parsing, feedback, reports and Streamlit flows. |
| Final affected regression tests | 23 passed after uploader-reset and PDF-font changes. `reports/targeted_tests.xml` records the executed parser and report/UI tests. This is a subset of the 59 tests, not 23 additional tests. |
| Static checks | `python -m ruff check .` passed on the final Python sources. |
| Dependencies | Runtime installation and `pip check` passed during the original build. No dependency versions changed in the final pass. Tested with Python 3.12.14. |
| Synthetic evaluation | Re-executed after rebuilding sample PDFs: 6/6 expected top roles, 6/6 normalized-text equivalence, micro skill precision 1.00 and recall 1.00. Four direct-text consistency probes also passed. |
| Browser acceptance | All 15 checks passed in Chromium 141.0.7390.37. Evidence: `reports/browser_verification.json`. |
| Visual review | Reviewed all four project-report pages, all three example-analysis pages, all three sample PDFs and the DOCX renders. Reviewed desktop and 390px mobile screenshots. |
| Submission hygiene | Targeted secret/unfinished-code scan returned no matches. Temporary failures, caches, virtual environments and discarded recordings are excluded from the package. |
| Package validation | ZIP integrity and extracted-package smoke checks passed: parsing, CSV loading, ranking and bundled-font PDF generation. Unix launcher passed `sh -n`. MP4 decoded successfully with FFmpeg. |

The final browser run exercised actual PDF upload, all three recommendations, target changes, skill gaps, roadmap, feedback, pasted and uploaded custom job descriptions, PDF download, DOCX replacement, methodology navigation, malformed-PDF recovery, session clearing and mobile layout. It reported no page errors or Streamlit exception overlays. Screenshots are in `docs/screenshots/`.

The font-only sample rebuild followed browser recording. The subsequent evaluation and 23 affected tests verify the rebuilt fixtures; analysis logic did not change. Caption DOM styles were also inspected: text uses RGB(78, 101, 107), not an unstyled light caption color.

## Final corrections

- Clear session now changes the uploader widget identity, clearing browser-side file state as well as analysis/report references. Repeated reset is covered by a regression assertion.
- PDF reports and fixtures embed bundled DejaVu fonts. This fixes inconsistent fallback-font rendering and keeps feedback headings with their first item.
- Responsive cards grow with their content; negative letter spacing and the decorative orbit were removed.

## Evaluation limits

The six files represent only **three manually authored fictional profiles**, each exported to PDF and DOCX. Their labels and profiles were created for this project. They are not six independent candidates or a representative benchmark. Perfect fixture results do not establish real-world accuracy, hiring outcomes, population fairness, or production performance. Protected-field probes are consistency tests, not a demographic fairness audit.

## Not executed or pending

- Docker/Compose files were inspected, but Docker was unavailable, so no container build/run is claimed.
- Windows launcher syntax was inspected; the app was executed on Linux, not on a Windows machine.
- GitHub publication requires explicit approval for a public repository. No repository was created and no GitHub Actions run is claimed.
- Streamlit Cloud/Render configuration and instructions are prepared. No hosted deployment or public application URL is claimed.

## Reproduce

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check .
python scripts/evaluate.py
```

Optional browser test, from the project root with Node.js and a working local Python environment:

```bash
npm install --no-save playwright@1.56.1
npx playwright install chromium
node scripts/verify_browser.mjs
```

The script starts and stops its own server on port 8512. `TEST_PYTHON` can select another virtual-environment interpreter. `BROWSER_EXECUTABLE` can select an installed Chromium. Its recorded WebM is an unedited acceptance run; the supplied MP4 is slowed for readability and has no narration.
