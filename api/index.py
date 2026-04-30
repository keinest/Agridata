"""Vercel entrypoint for the Flask backend."""
import sys
from pathlib import Path

# Ensure project root is on sys.path so backend.app.* imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app  # noqa: E402 — must come after sys.path patch
