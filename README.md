# Tourist Routes Manager

Консольний застосунок для керування туристичними маршрутами (Python) з аналітикою даних у Pandas та візуалізацією (Matplotlib, Seaborn).

## Можливості

- **Керування маршрутами:** додавання, перегляд, пошук (ID / назва / країна), фільтри (тип / протяжність / середній бал), сортування, редагування, видалення, статистика.
- **Типи маршрутів (ООП):** `Route`, `HikingRoute`, `CyclingRoute`, `BusTour` з валідацією даних і поліморфним розрахунком тривалості.
- **Збереження:** JSON-сховище, експорт у CSV.
- **Аналітика (Pandas):** завантаження CSV, очищення, нові стовпці, групування, збереження результатів.
- **Візуалізація:** 19 графіків (розподіли, викиди, категорії, кореляції, групування, динаміка в часі) з висновками.
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
- **REST API (FastAPI):** повний CRUD для маршрутів, пошук і фільтрація, база даних SQLite (SQLAlchemy), JWT-автентифікація, CORS, Swagger UI.
>>>>>>> Stashed changes
=======
- **Telegram-бот:** каталог, пошук, фільтр за типом, топ за оцінкою, обране користувача; працює як клієнт REST API.
- **REST API (FastAPI):** повний CRUD для маршрутів, пошук і фільтрація, база даних SQLite (SQLAlchemy), JWT-автентифікація, CORS, Swagger UI.
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
>>>>>>> Stashed changes
│   ├── api/                       # REST API (FastAPI)
│   │   ├── main.py                #   застосунок, CORS, підключення роутерів
│   │   ├── config.py  database.py #   налаштування, підключення до БД (SQLAlchemy)
│   │   ├── security.py            #   хешування паролів, JWT
│   │   ├── dependencies.py        #   get_current_user (захист endpoints)
│   │   ├── models/                #   ORM-моделі: RouteRecord, User
│   │   ├── schemas/               #   Pydantic-схеми: RouteCreate/RouteRead, UserCreate, Token
│   │   └── routers/               #   auth.py, routes.py
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
│   ├── bot/                       # Telegram-бот (клієнт REST API)
│   │   ├── app.py                 #   збирання й запуск, реєстрація обробників
│   │   ├── handlers.py            #   команди, текст, кнопки, обробка помилок
│   │   ├── keyboards.py           #   inline-клавіатури
│   │   ├── formatting.py          #   форматування відповідей
│   │   ├── api_client.py          #   взаємодія з REST API (httpx)
│   │   ├── storage.py             #   обране користувачів (SQLite)
│   │   └── config.py
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
│   └── generate_dataset.py        # перегенерація датасету
└── tests/
    └── test_analytics.py
=======
│   ├── run_api.py                 # запуск REST API (uvicorn)
│   └── generate_dataset.py        # перегенерація датасету
└── tests/
    ├── test_analytics.py
    └── test_api.py
>>>>>>> Stashed changes
=======
│   ├── run_api.py                 # запуск REST API (uvicorn)
│   ├── run_bot.py                 # запуск Telegram-бота
│   └── generate_dataset.py        # перегенерація датасету
└── tests/
    ├── test_analytics.py
    ├── test_api.py
    └── test_bot.py
>>>>>>> Stashed changes
```

## Запуск

```bash
pip install -r requirements.txt

python main.py                          # консольний застосунок (меню українською)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
uvicorn tourist_routes.api.main:app --reload   # REST API: http://127.0.0.1:8000/docs
>>>>>>> Stashed changes
=======
uvicorn tourist_routes.api.main:app --reload   # REST API: http://127.0.0.1:8000/docs
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
>>>>>>> Stashed changes

## REST API

Запуск: `uvicorn tourist_routes.api.main:app --reload` (або `python scripts/run_api.py`), документація — `http://127.0.0.1:8000/docs`. При першому запуску створюється `data/api.db` (SQLite) і додаються демо-маршрути.

| Метод | Шлях | Опис | Доступ |
|---|---|---|---|
| GET | `/` | повідомлення про роботу API | відкрито |
| POST | `/auth/register` | реєстрація (201, 409 якщо ім'я зайняте) | відкрито |
| POST | `/auth/login` | вхід (form-data `username`, `password`) → JWT | відкрито |
| GET | `/auth/me` | поточний користувач | JWT |
| GET | `/routes` | список; фільтри `name`, `country`, `type`, `min_length_km`, `max_length_km`, `skip`, `limit` | відкрито |
| GET | `/routes/{id}` | один маршрут (404, якщо немає) | відкрито |
| POST | `/routes` | створення (201) | JWT |
| PUT | `/routes/{id}` | повна заміна даних | JWT |
| DELETE | `/routes/{id}` | видалення (204) | JWT |

Без дійсного токена захищені endpoints повертають `401 Unauthorized`; некоректні дані — `422`. Для авторизації в Swagger UI натисніть **Authorize** і введіть логін/пароль.

Змінні середовища: `SECRET_KEY` (обов'язково змініть поза навчальним запуском), `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS` (через кому).

Приклад:

```bash
curl -X POST http://127.0.0.1:8000/auth/register -H "Content-Type: application/json" -d '{"username":"traveler","password":"secret123"}'
curl -X POST http://127.0.0.1:8000/auth/login -d "username=traveler&password=secret123"
curl -X POST http://127.0.0.1:8000/routes -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"type":"Route","name":"Прогулянка","country":"Україна","start_city":"Львів","length_km":5,"description":"Центр міста"}'
```
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======

## Telegram-бот

Бот допомагає обирати туристичні маршрути й працює як **клієнт REST API** (дані беруться з `/routes`).

**Запуск**
1. У Telegram напишіть [@BotFather](https://t.me/BotFather), створіть бота командою `/newbot` і скопіюйте токен.
2. Запустіть API (`python -m uvicorn tourist_routes.api.main:app --reload`) в одному терміналі.
3. У другому терміналі задайте токен і запустіть бота:

```powershell
$env:TELEGRAM_BOT_TOKEN = "ВАШ_ТОКЕН"      # PowerShell
python -m tourist_routes.bot
```
(у cmd: `set TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН`, у Linux/macOS: `export TELEGRAM_BOT_TOKEN=...`)

Необов'язкові змінні: `ROUTES_API_URL` (за замовчуванням `http://127.0.0.1:8000`), `ROUTES_API_TIMEOUT`, `BOT_DB_FILE`.

**Команди й дії**

| Команда / кнопка | Що робить |
|---|---|
| `/start` | привітання й головне меню (inline-кнопки) |
| `/help` | перелік команд |
| `/routes` | каталог маршрутів із кнопками для перегляду деталей |
| `/search назва` або просто текст | пошук за назвою |
| `/types` | вибір типу маршруту кнопками |
| `/top` | найвище оцінені маршрути |
| `/favorites`, кнопка «⭐ В обране» | обране користувача (зберігається в SQLite `data/bot.db`) |

Обробка помилок: якщо API недоступне, не відповідає вчасно, повертає помилку або неповні дані — користувач отримує зрозуміле повідомлення, бот продовжує працювати. Невідомі команди й некоректні кнопки теж обробляються.
>>>>>>> Stashed changes
