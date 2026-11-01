"""Запускає REST API:  python scripts/run_api.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run("tourist_routes.api.main:app", host="127.0.0.1", port=8000, reload=True)
