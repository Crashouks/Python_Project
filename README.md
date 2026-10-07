# Tourist Routes Manager

A console application for managing a collection of tourist routes, written in pure Python with no external dependencies.

Lab 1 — *Creating a basic Python application: functions, lists, tuples and dictionaries* (variant 8: tourist routes).

> The application interface (menu and prompts) is in Ukrainian.

## Features

- Add, edit and delete routes
- Show all routes
- Search by ID, name or country
- Filter by length range or minimum average rating
- Sort by average rating or by length
- Statistics: number of routes, average length, longest and shortest route, rating summary, best-rated route, routes per country
- Input validation with re-prompting on errors
- When editing, press Enter to keep the current value of a field
- Preloaded sample data for quick testing

## Data model

Each route is a dictionary:

| Field         | Type                          | Description                      |
|---------------|-------------------------------|----------------------------------|
| `name`        | `str`                         | Route name                       |
| `ratings`     | `list[int \| float]`          | Tourist reviews (scores 1–10)    |
| `location`    | `tuple[str, str]`             | `(country, start city)`          |
| `length_km`   | `float`                       | Route length in kilometers       |
| `description` | `str`                         | Route description                |

Routes are stored in a dictionary `{route_id: route}`, so IDs stay stable after deletions.

## Project structure

```
tourist_routes/
├── main.py          # entry point
├── config.py        # constants (rating limits, thresholds)
├── models.py        # route creation and calculations
├── repository.py    # in-memory storage (add, find, replace, remove, select)
├── services.py      # search, filters, sorting, statistics
├── input_utils.py   # reading and validating user input
├── display.py       # printing routes and statistics
├── actions.py       # menu handlers
├── menu.py          # menu definition and main loop
└── sample_data.py   # demo routes
```

The code is layered: `services` contains logic only, `display` handles output only, and `actions` connects them to user input.

## Requirements

- Python 3.8 or newer

## Run

```bash
git clone <your-repository-url>
cd tourist_routes
python main.py
```

## Menu

```
==== Туристичні маршрути ====
1. Додати маршрут
2. Показати всі маршрути
3. Пошук за ID
4. Пошук за назвою
5. Пошук за країною
6. Фільтр за протяжністю
7. Фільтр за середнім балом
8. Сортувати за рейтингом
9. Сортувати за протяжністю
10. Редагувати маршрут
11. Видалити маршрут
12. Статистика
0. Вихід
```

## Extending the project

- **New menu item:** write a handler in `actions.py` and add one line to `MENU_ITEMS` in `menu.py`.
- **New route field:** add it to `create_route` in `models.py`, to `read_route_data` in `input_utils.py`, and to `print_route` in `display.py`.
- **New search or filter:** add a function to `services.py` built on `select_routes`, then a handler in `actions.py`.
- **Different storage (file, database):** replace the functions in `repository.py`; the rest of the code does not depend on how routes are stored.
