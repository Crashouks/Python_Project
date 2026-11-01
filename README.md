# Tourist Routes Manager

Консольний застосунок для керування туристичними маршрутами (Python) з аналітикою даних у Pandas та візуалізацією (Matplotlib, Seaborn).

## Можливості

- **Керування маршрутами:** додавання, перегляд, пошук (ID / назва / країна), фільтри (тип / протяжність / середній бал), сортування, редагування, видалення, статистика.
- **Типи маршрутів (ООП):** `Route`, `HikingRoute`, `CyclingRoute`, `BusTour` з валідацією даних і поліморфним розрахунком тривалості.
- **Збереження:** JSON-сховище, експорт у CSV.
- **Аналітика (Pandas):** завантаження CSV, очищення, нові стовпці, групування, збереження результатів.
- **Візуалізація:** 19 графіків (розподіли, викиди, категорії, кореляції, групування, динаміка в часі) з висновками.

## Структура

```
Python_Project/
├── main.py                        # запуск консольного застосунку
├── requirements.txt
├── tourist_routes/
│   ├── core/                      # предметна область
│   │   ├── config.py              #   константи й межі значень
│   │   ├── models.py              #   Route, HikingRoute, CyclingRoute, BusTour
│   │   ├── validators.py          #   перевірка даних
│   │   ├── factory.py             #   створення маршруту за типом
│   │   ├── manager.py             #   колекція маршрутів: пошук, фільтри, сортування
│   │   ├── route_statistics.py    #   статистика
│   │   ├── sample_data.py         #   демо-маршрути
│   │   └── exceptions.py
│   ├── storage/
│   │   └── json_storage.py        # збереження/завантаження JSON
│   ├── cli/                       # консольний інтерфейс
│   │   └── app.py  menu.py  display.py  input_reader.py  route_form.py
│   └── analytics/                 # робота з даними (Pandas)
│       ├── generate_dataset.py    #   генерація «брудного» CSV (NumPy)
│       ├── cleaning.py            #   дублікати, пропуски, текст, типи
│       ├── features.py            #   нові стовпці (середній бал, тривалість...)
│       ├── analysis.py            #   групування та агрегація
│       ├── converters.py          #   Route -> DataFrame
│       └── pipeline.py            #   повний конвеєр CSV -> CSV
├── notebooks/
│   ├── data_processing.ipynb      # обробка даних у Pandas
│   └── data_visualization.ipynb   # візуалізація (19 графіків, висновки)
├── figures/                       # PNG-графіки (01_histograms.png ... 19_pairplot.png)
├── data/
│   ├── raw/routes_dataset.csv     # вхідний датасет
│   └── processed/                 # processed_routes.csv, grouped_country_type.csv
├── scripts/
│   ├── demo.py                    # демо роботи з класами маршрутів
│   ├── run_pipeline.py            # конвеєр очищення й аналізу даних
│   ├── build_figures.py           # виконання ноутбука візуалізації, збереження графіків
│   └── generate_dataset.py        # перегенерація датасету
└── tests/
    └── test_analytics.py
```

## Запуск

```bash
pip install -r requirements.txt

python main.py                          # консольний застосунок (меню українською)
python scripts/demo.py                  # демо класів маршрутів
python scripts/run_pipeline.py          # очищення й аналіз датасету -> data/processed/
python scripts/build_figures.py         # перегенерувати всі графіки у figures/
jupyter notebook notebooks/data_processing.ipynb
jupyter notebook notebooks/data_visualization.ipynb
python -m unittest discover -s tests    # тести
```

Консольний застосунок працює і без pandas; пункти меню **«Аналіз даних (Pandas)»** та **«Експорт у CSV»** потребують `pip install -r requirements.txt`.

## Дані й аналітика

- Датасет `data/raw/routes_dataset.csv`: 312 рядків × 14 стовпців; структура повторює класи маршрутів; містить навмисні дефекти (пропуски, дублікати, зайві пробіли, некоректні числа/дати/оцінки).
- Очищення: дублікати, текст, кома → крапка, неможливі довжини, пропуски (медіана за типом), оцінки поза 1–10; приведення типів (`category`, `datetime`, `Int64`).
- Нові стовпці: середній бал, кількість відгуків, тривалість, ціна за км, категорія довжини, випадковий бал популярності.
- Аналіз: `describe`, розподіл категорій, фільтрація, сортування, групування за однією та двома змінними, зведена таблиця.
- Інтеграція: меню застосунку аналізує/експортує поточні маршрути через pandas, а тест звіряє pandas-розрахунки з методами класів `Route`.
- Візуалізація: гістограми з KDE, Box/Violin Plot, Count/Pie/Bar, Scatter із трендами, матриця кореляцій, Pair Plot, теплові карти, Line Plot у часі; датасет згенеровано, тому деякі залежності в ньому свідомо слабкі — це зазначено у висновках.
