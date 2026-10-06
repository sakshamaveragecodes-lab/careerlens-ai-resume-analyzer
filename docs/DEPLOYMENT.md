# Deployment guide

The package is deployable without API keys or a database. Deployment needs a GitHub repository and an authenticated hosting account. This guide describes the configured route; `VERIFICATION.md` records whether a live deployment was actually completed.

## GitHub

Create a repository named `careerlens-resume-analyzer` under your own account. Keep `app.py`, `requirements.txt`, `data`, `src` and `.streamlit` at the repository root. Do not upload the outer ZIP, a virtual environment, `.env`, private resumes or downloaded private reports. The provided fixtures are fictional and safe to publish.

If starting from the extracted directory with Git installed:

```bash
git init -b main
git add .
git commit -m "Build CareerLens resume analyzer"
```

Connect the remote URL shown by your newly created repository, then push `main`. The exact URL must come from your account; no repository URL is fabricated in this package. The included GitHub Actions workflow runs lint, tests and synthetic evaluation on pushes and pull requests.

## Streamlit Community Cloud

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in to your own account.
2. Grant the repository access needed by the hosting service if it is not already connected.
3. Choose **Create app**, select the repository and `main`, and set the main file to **`app.py`**.
4. In advanced settings, use **Python 3.12**. No secrets are needed.
5. Deploy and wait for dependency installation. Then test a PDF, a DOCX, role switching, custom JD comparison and PDF download on the published URL.
6. Verify the visible URL from the deployment result before sharing it. Set the desired app access in the hosting UI.

The application uses `requirements.txt`, `.streamlit/config.toml`, and relative paths resolved from the project root. The lock file is also available for stricter reproducibility. If you change CSV data, restart the app to refresh cached resources.

## Render

Use the included `render.yaml` Blueprint after connecting the repository, or configure a Python web service:

| Setting | Value |
| --- | --- |
| Build command | `pip install -r requirements.lock.txt` |
| Start command | `python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT` |
| Python | 3.12 |
| Health endpoint | `/_stcore/health` |
| Environment | `MAX_UPLOAD_MB=5` |
| Persistent disk | Not required |

The Blueprint requests the free plan. Plan availability, sleeping behavior and limits depend on the host at deployment time. Do not select a paid tier without reviewing its cost.

## Docker hosting

```bash
docker build -t careerlens .
docker run --rm -p 8501:8501 -e MAX_UPLOAD_MB=5 careerlens
```

Or run `docker compose up --build`. Open http://localhost:8501. The image runs as UID 10001 and uses a health check. Terminate the container to discard in-memory sessions. A reverse proxy must support WebSockets; terminate TLS at the host/proxy and keep Streamlit XSRF protection enabled. Sticky sessions may be needed for multiple replicas because analysis is intentionally not shared.

## Pre-launch checks

Run `python -m pytest -q`, `python -m ruff check .`, and `python scripts/evaluate.py` from the project root after installing development requirements. Confirm that only fictional data is included in the repository. Review the host's own logging and retention settings before sharing the app with real users.

No database migrations are required. No `.env` secret is required. No external AI service needs authorization.

## Reference documentation

- [Streamlit Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
- [Streamlit dependency management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Render web services](https://render.com/docs/web-services)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
