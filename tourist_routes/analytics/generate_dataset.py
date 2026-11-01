"""Генерація навчального датасету туристичних маршрутів (CSV).

Структура стовпців повторює модель предметної області (Route, HikingRoute, CyclingRoute, BusTour).
У дані навмисно додаються "брудні" записи (пропуски, дублікати, зайві пробіли,
некоректні числа), щоб на етапі очищення було що виправляти.

Запуск:  python scripts/generate_dataset.py
Результат: data/raw/routes_dataset.csv
"""
import os

import numpy as np
import pandas as pd

SEED = 42
N_ROWS = 300
OUTPUT_FILE = "data/raw/routes_dataset.csv"

COUNTRIES = {
    "Україна": ["Ворохта", "Львів", "Яремче", "Одеса", "Київ", "Буковель"],
    "Польща": ["Закопане", "Краків", "Гданськ", "Вроцлав"],
    "Словаччина": ["Попрад", "Братислава", "Кошице"],
    "Австрія": ["Пассау", "Зальцбург", "Інсбрук", "Відень"],
    "Франція": ["Шамоні", "Ліон", "Ніцца", "Страсбург"],
    "Італія": ["Болцано", "Верона", "Кортіна", "Рим"],
    "Швейцарія": ["Церматт", "Інтерлакен", "Люцерн"],
    "Перу": ["Куско", "Арекіпа"],
    "Норвегія": ["Ставангер", "Берген", "Одда"],
}

PLACES = ["Карпат", "Дунаю", "Татр", "Альп", "Монблану", "Фйордів", "Анд", "Дністра",
          "Балтики", "Доломітів", "Старого міста", "Озерного краю"]
TEMPLATES = {
    "HikingRoute": ["Піший похід {p}", "Стежка {p}", "Трек через {p}", "Хребтами {p}"],
    "CyclingRoute": ["Веломаршрут {p}", "Велотур {p}", "Трейл {p}", "Велопетля {p}"],
    "BusTour": ["Автотур {p}", "Автобусом через {p}", "Екскурсійний тур {p}"],
    "Route": ["Прогулянка {p}", "Оглядова екскурсія {p}", "Маршрут вихідного дня: {p}"],
}
DESCRIPTIONS = [
    "Мальовничий маршрут з чудовими краєвидами.",
    "Підходить для підготовлених туристів.",
    "Популярний маршрут у літній сезон.",
    "Є кемпінги та місця для відпочинку по дорозі.",
    "Маршрут проходить через національний парк.",
    "Зручний варіант для вихідних.",
]
DIFFICULTIES = ["легкий", "середній", "складний"]
BIKE_TYPES = ["шосейний", "гірський", "міський"]
TYPE_WEIGHTS = {"HikingRoute": 0.35, "CyclingRoute": 0.25, "BusTour": 0.2, "Route": 0.2}


def make_ratings(rng, quality):
    count = int(rng.integers(2, 8))
    scores = np.clip(np.round(rng.normal(quality, 1.2, count)), 1, 10).astype(int)
    return " ".join(map(str, scores))


def build_clean_rows(rng):
    types = rng.choice(list(TYPE_WEIGHTS), size=N_ROWS, p=list(TYPE_WEIGHTS.values()))
    countries = list(COUNTRIES)
    rows = []
    for route_type in types:
        country = str(rng.choice(countries))
        city = str(rng.choice(COUNTRIES[country]))
        place = str(rng.choice(PLACES))
        name = f"{rng.choice(TEMPLATES[route_type]).format(p=place)} ({city})"
        length = {"HikingRoute": rng.uniform(5, 80), "CyclingRoute": rng.uniform(30, 350),
                  "BusTour": rng.uniform(80, 900), "Route": rng.uniform(2, 15)}[route_type]
        row = {
            "type": route_type,
            "name": name,
            "country": country,
            "start_city": city,
            "length_km": round(float(length), 1),
            "description": str(rng.choice(DESCRIPTIONS)),
            "ratings": make_ratings(rng, rng.uniform(6.5, 9.5)),
            "difficulty": None,
            "elevation_gain_m": None,
            "bike_type": None,
            "stops_count": None,
            "date_added": (pd.Timestamp("2023-01-01")
                           + pd.Timedelta(days=int(rng.integers(0, 1100)))).strftime("%Y-%m-%d"),
            "price_eur": round(float(rng.uniform(0, 40) if route_type == "Route"
                                     else rng.uniform(20, 600)), 2),
        }
        if route_type == "HikingRoute":
            row["difficulty"] = str(rng.choice(DIFFICULTIES))
            row["elevation_gain_m"] = int(rng.integers(100, 3000))
        elif route_type == "CyclingRoute":
            row["bike_type"] = str(rng.choice(BIKE_TYPES))
        elif route_type == "BusTour":
            row["stops_count"] = int(rng.integers(2, 15))
        rows.append(row)
    return pd.DataFrame(rows)


def add_dirt(df, rng):
    """Вносить типові дефекти реальних даних."""
    df = df.astype({"length_km": object, "price_eur": object, "ratings": object,
                    "description": object, "date_added": object})
    df.insert(0, "route_id", range(1, len(df) + 1))
    n = len(df)
    pick = lambda k: rng.choice(n, size=k, replace=False)

    df.loc[pick(15), "price_eur"] = np.nan          # пропущені ціни
    df.loc[pick(10), "description"] = np.nan        # пропущені описи
    df.loc[pick(8), "ratings"] = np.nan             # маршрути без відгуків
    df.loc[pick(6), "length_km"] = np.nan           # пропущена довжина

    for i in pick(12):                              # зайві пробіли / регістр
        df.loc[i, "country"] = f"  {str(df.loc[i, 'country']).upper()} "
    for i in pick(10):
        df.loc[i, "name"] = f" {df.loc[i, 'name'].lower()}  "
    for i in pick(8):                               # кома замість крапки
        if pd.notna(df.loc[i, "length_km"]):
            df.loc[i, "length_km"] = str(df.loc[i, "length_km"]).replace(".", ",")

    df.loc[pick(4), "length_km"] = -25.0            # некоректні значення
    df.loc[pick(3), "length_km"] = 99999.0
    for i in pick(4):
        df.loc[i, "ratings"] = "9 15 8"             # бал поза діапазоном 1-10
    df.loc[pick(3), "date_added"] = "не вказано"    # некоректна дата
    df.loc[pick(3), "price_eur"] = -10.0

    duplicates = df.iloc[pick(12)]                  # повні дублікати рядків
    df = pd.concat([df, duplicates], ignore_index=True)
    return df.sample(frac=1, random_state=SEED).reset_index(drop=True)


def generate(output_file=OUTPUT_FILE):
    rng = np.random.default_rng(SEED)
    df = add_dirt(build_clean_rows(rng), rng)
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8")
    return df


def main():
    df = generate()
    print(f"Збережено {len(df)} рядків у {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
