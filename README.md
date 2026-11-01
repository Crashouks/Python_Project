# Tourist Routes Manager

Консольний застосунок для керування туристичними маршрутами (Python) з аналітикою даних у Pandas.

| Лабораторна | Тема | Де в проєкті |
|---|---|---|
| ЛР 1 | Функції, списки, кортежі, словники | `tourist_routes/core`, `tourist_routes/cli` |
| ЛР 2 | ООП: класи маршрутів, валідація, JSON-сховище | `tourist_routes/core/models.py`, `tourist_routes/storage` |
| ЛР 3 | Pandas: CSV, очищення, аналіз, групування | `tourist_routes/analytics`, `notebooks/Lab3.ipynb`, `data/` |
| ЛР 4 | Візуалізація: Matplotlib, Seaborn | `notebooks/Lab4.ipynb`, `figures/` |

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
│   ├── Lab3.ipynb                # ЛР 3: обробка даних у Pandas
│   └── Lab4.ipynb                # ЛР 4: візуалізація даних (19 графіків, висновки)
├── figures/                      # PNG-графіки ЛР 4 (01_histograms.png ... 19_pairplot.png)
├── data/
│   ├── raw/routes_dataset.csv    # вхідний датасет
│   └── processed/                # результати: processed_routes.csv, grouped_country_type.csv
├── scripts/
│   ├── demo.py                   # демо ЛР 2
│   ├── run_lab3.py               # запуск конвеєра ЛР 3
│   ├── run_lab4.py               # виконання ноутбука ЛР 4 і збереження графіків
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
jupyter notebook notebooks/Lab4.ipynb   # ЛР 4: графіки та висновки
python scripts/run_lab4.py        # ЛР 4: перегенерувати всі графіки у figures/
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

## ЛР 4: що реалізовано

Ноутбук `notebooks/Lab4.ipynb` працює з очищеним датасетом із ЛР 3 і містить 19 графіків (PNG у `figures/`):

- **Розподіли:** гістограми з KDE (лінійна й логарифмічна шкала), KDE за типами маршрутів.
- **Box Plot і викиди:** загальні та за типами, IQR-аналіз у всій вибірці та в межах типу, обґрунтування, чому викиди не видаляються; Violin Plot.
- **Категорії:** Count Plot, Pie Chart, Bar Chart із довірчими інтервалами.
- **Взаємозв'язки:** Scatter Plot із трендовими лініями (у т.ч. log–log), матриця кореляцій + Heatmap, Pair Plot.
- **Групування:** `groupby` за типом, країною, категорією протяжності; теплова карта «країна × тип».
- **Час:** Line Plot кількості нових маршрутів (з ковзним середнім, піком і спадом) та середнього балу.
- **Висновки** за кожним розділом і загальні; окремо зазначено, що датасет згенерований.

## Меню застосунку

Додавання, перегляд, пошук (ID / назва / країна), фільтри (тип / протяжність / середній бал), сортування (рейтинг / протяжність / тривалість), редагування, видалення, статистика, збереження/завантаження JSON, **аналіз у Pandas**, **експорт у CSV**.
