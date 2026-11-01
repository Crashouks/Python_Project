"""Запускає повний конвеєр обробки даних:  python scripts/run_pipeline.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tourist_routes.analytics.pipeline import run  # noqa: E402

if __name__ == "__main__":
    run(ROOT / "data/raw/routes_dataset.csv", ROOT / "data/processed")
