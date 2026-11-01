"""Виконує ноутбук візуалізації без браузера й зберігає всі графіки в figures/:  python scripts/build_figures.py"""
import sys
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "notebooks" / "data_visualization.ipynb"


def main():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    ExecutePreprocessor(timeout=600, kernel_name="python3").preprocess(
        notebook, {"metadata": {"path": str(NOTEBOOK.parent)}}
    )
    nbformat.write(notebook, NOTEBOOK)
    figures = sorted((ROOT / "figures").glob("*.png"))
    print(f"Ноутбук виконано. Збережено графіків: {len(figures)} у {ROOT / 'figures'}")


if __name__ == "__main__":
    sys.exit(main())
