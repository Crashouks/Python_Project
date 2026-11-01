"""Повний конвеєр ЛР 3: сирий CSV -> очищення -> нові стовпці -> групування -> збереження."""
from pathlib import Path

import pandas as pd

from tourist_routes.analytics import analysis
from tourist_routes.analytics.cleaning import clean
from tourist_routes.analytics.features import add_features
from tourist_routes.analytics.generate_dataset import generate

RAW_FILE = Path("data/raw/routes_dataset.csv")
PROCESSED_DIR = Path("data/processed")


def run(raw_file=RAW_FILE, processed_dir=PROCESSED_DIR, verbose=True):
    log = print if verbose else (lambda *a, **k: None)
    raw_file, processed_dir = Path(raw_file), Path(processed_dir)

    if not raw_file.exists():
        log(f"Файл {raw_file} не знайдено — генеруємо датасет.")
        generate(str(raw_file))

    raw = pd.read_csv(raw_file)
    log(f"Зчитано: {raw.shape[0]} рядків, {raw.shape[1]} стовпців ({raw_file})")
    log(f"Пропусків у сирих даних: {int(raw.isnull().sum().sum())}, дублікатів: {int(raw.duplicated().sum())}")

    df = add_features(clean(raw))
    log(f"Після очищення: {df.shape[0]} рядків, {df.shape[1]} стовпців")

    processed_dir.mkdir(parents=True, exist_ok=True)
    processed_file = processed_dir / "processed_routes.csv"
    grouped_file = processed_dir / "grouped_country_type.csv"
    df.drop(columns=["ratings_list"]).to_csv(processed_file, index=False, encoding="utf-8")
    grouped = analysis.by_country_and_type(df)
    grouped.to_csv(grouped_file, index=False, encoding="utf-8")

    log("\nГрупування за типом маршруту:")
    log(analysis.by_type(df).to_string())
    log("\nГрупування за країною (топ-5 за кількістю):")
    log(analysis.by_country(df).head().to_string())
    log(f"\nЗбережено: {processed_file}, {grouped_file}")
    return df, grouped
