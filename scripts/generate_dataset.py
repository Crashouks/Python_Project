"""Генерує сирий датасет:  python scripts/generate_dataset.py"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from tourist_routes.analytics.generate_dataset import main  # noqa: E402

if __name__ == "__main__":
    main()
