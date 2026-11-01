# Tourist Routes Manager

Консольний застосунок для керування туристичними маршрутами (Python) з аналітикою даних у Pandas.

| Лабораторна | Тема | Де в проєкті |
|---|---|---|
| ЛР 1 | Функції, списки, кортежі, словники | `tourist_routes/core`, `tourist_routes/cli` |
| ЛР 2 | ООП: класи маршрутів, валідація, JSON-сховище | `tourist_routes/core/models.py`, `tourist_routes/storage` |
| ЛР 3 | Pandas: CSV, очищення, аналіз, групування | `tourist_routes/analytics`, `notebooks/Lab3.ipynb`, `data/` |

## Структура

```
Python_Project/
├── main.py                       # запуск консольного застосунку
├── requirements.txt
├── tourist_routes/
│   ├── core/                     # предметна область (ЛР 1–2)
│   │   ├── config.py             #   константи й межі значень
│   │   ├── models.py             #   Route, HikingRoute, CyclingRoute, BusTour
│   │   ├── validators.py         #   перевірка даних
│   │   ├── factory.py            #   створення маршруту за типом
│   │   ├── manager.py            #   колекція маршрутів: пошук, фільтри, сортування
│   │   ├── route_statistics.py   #   статистика
│   │   ├── sample_data.py        #   демо-маршрути
│   │   └── exceptions.py
│   ├── storage/
│   │   └── json_storage.py       # збереження/завантаження JSON
│   ├── cli/                      # консольний інтерфейс
│   │   ├── app.py  menu.py  display.py  input_reader.py  route_form.py
│   └── analytics/                # ЛР 3 (Pandas)
│       ├── generate_dataset.py   #   генерація «брудного» CSV (NumPy)
│       ├── cleaning.py           #   дублікати, пропуски, текст, типи
│       ├── features.py           #   нові стовпці (середній бал, тривалість...)
│       ├── analysis.py           #   групування та агрегація
│       ├── converters.py         #   Route (ЛР 2) -> DataFrame
│       └── pipeline.py           #   повний конвеєр CSV -> CSV
├── notebooks/
│   └── Lab3.ipynb                # ноутбук ЛР 3 з виводами (Jupyter / Colab)
├── data/
│   ├── raw/routes_dataset.csv    # вхідний датасет
│   └── processed/                # результати: processed_routes.csv, grouped_country_type.csv
├── scripts/
│   ├── demo.py                   # демо ЛР 2
│   ├── run_lab3.py               # запуск конвеєра ЛР 3
│   └── generate_dataset.py       # перегенерація датасету
└── tests/
    └── test_lab3.py
```

## Запуск

```bash
pip install -r requirements.txt

python main.py                    # консольний застосунок (меню українською)
python scripts/run_lab3.py        # ЛР 3: очищення й аналіз датасету -> data/processed/
jupyter notebook notebooks/Lab3.ipynb   # ЛР 3 у вигляді ноутбука
python scripts/demo.py            # демо ЛР 2
python -m unittest discover -s tests    # тести
```

Консольний застосунок працює і без pandas; пункти меню **«Аналіз даних (Pandas)»** та **«Експорт у CSV»** потребують `pip install -r requirements.txt`.

## ЛР 3: що реалізовано

- Датасет `data/raw/routes_dataset.csv`: 312 рядків × 14 стовпців; структура повторює класи з ЛР 2; містить навмисні дефекти (пропуски, дублікати, зайві пробіли, некоректні числа/дати/оцінки).
- Очищення: дублікати, текст, кома → крапка, неможливі довжини, пропуски (медіана за типом), оцінки поза 1–10; приведення типів (`category`, `datetime`, `Int64`).
- Нові стовпці: середній бал, кількість відгуків, тривалість (за правилами ЛР 2), ціна за км, категорія довжини, випадковий бал популярності.
- Аналіз: `describe`, розподіл категорій, фільтрація (`&`, `|`), сортування, групування за однією та двома змінними, зведена таблиця.
- Збереження: `processed_routes.csv`, `grouped_country_type.csv` (+ перевірка читанням).
- Інтеграція з ЛР 2: меню застосунку аналізує/експортує поточні маршрути через pandas, а тест звіряє pandas-розрахунки з методами класів `Route`.

## Меню застосунку

Додавання, перегляд, пошук (ID / назва / країна), фільтри (тип / протяжність / середній бал), сортування (рейтинг / протяжність / тривалість), редагування, видалення, статистика, збереження/завантаження JSON, **аналіз у Pandas**, **експорт у CSV**.
