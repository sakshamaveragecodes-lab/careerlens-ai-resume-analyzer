"""Configuration is bounded so an environment typo cannot disable safeguards."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)


def bounded_int(name: str, default: int, low: int, high: int) -> int:
    try:
        return max(low, min(high, int(os.getenv(name, str(default)))))
    except ValueError:
        return default


MAX_UPLOAD_MB = bounded_int("MAX_UPLOAD_MB", 5, 1, 10)
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
MAX_PAGES = 20
MAX_TEXT_CHARS = 150_000
DATA_DIR = ROOT / "data"
DISCLAIMER = (
    "Match scores are estimates of documented skill alignment, not recruiter decisions "
    "or hiring probabilities. This tool supports career guidance, never automatic hiring "
    "or rejection. Not detected in the resume does not mean a skill is absent."
)
