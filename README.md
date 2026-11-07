# Tourist Routes Manager

Python application for managing tourist routes, processing route datasets, and
exploring them through a CLI, REST API, or Telegram bot.

## Features

- Route models for `Route`, `HikingRoute`, `CyclingRoute`, and `BusTour`, with
  validation, search, filtering, sorting, and statistics.
- JSON persistence and CSV export.
- Pandas data cleaning, feature generation, analysis, and visualizations.
- FastAPI CRUD API with SQLite, SQLAlchemy, JWT authentication, and Swagger UI.
- Telegram bot for browsing routes, searching, filtering by type, viewing
  top-rated routes, and saving user favorites in SQLite.
- Web scraping utilities, including a scraper for Books to Scrape.

## Install

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py                                  # CLI
python scripts/demo.py                          # route model demo
python scripts/run_pipeline.py                  # process and analyze route data
python scripts/build_figures.py                  # regenerate figures
python scripts/run_scraper.py                    # scraper demo
python -m uvicorn tourist_routes.api.main:app --reload
```

The API documentation is available at `http://127.0.0.1:8000/docs`.
On first startup, the API creates `data/api.db` and loads sample routes.

## Telegram bot

The bot is an API client, so start the REST API before starting the bot. Create
a bot with [@BotFather](https://t.me/BotFather), then set its token and run:

```powershell
$env:TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
python -m tourist_routes.bot
```

For Command Prompt, use `set TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN`; for
Linux/macOS, use `export TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN`.

On Windows, you can instead double-click [`scripts/launch_bot.bat`](scripts/launch_bot.bat).
The launcher securely prompts for the token on first use and saves it in the
git-ignored `.env` file for later launches. The `.env` file stores the test
token as plain text on this computer; do not share it. If the token changes,
delete `.env` to be prompted again. The launcher starts the API if it is not
already responding, then opens the bot in its own terminal. Close any
already-running copy of the bot before launching another one.

Optional settings:

- `ROUTES_API_URL` (default `http://127.0.0.1:8000`)
- `ROUTES_API_TIMEOUT` (default `10` seconds)
- `BOT_DB_FILE` (default `data/bot.db`)

Bot commands include `/start`, `/help`, `/routes`, `/search <name>`, `/types`,
`/top`, and `/favorites`. Users can also search by sending plain text and add
or remove routes from favorites using the inline buttons. API failures are
reported to the user without stopping the bot.

## REST API

| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/` | Public | API status |
| POST | `/auth/register` | Public | Register a user |
| POST | `/auth/login` | Public | Get a JWT |
| GET | `/auth/me` | JWT | Current user |
| GET | `/routes` | Public | List, search, and filter routes |
| GET | `/routes/{id}` | Public | Get one route |
| POST | `/routes` | JWT | Create a route |
| PUT | `/routes/{id}` | JWT | Replace a route |
| DELETE | `/routes/{id}` | JWT | Delete a route |

Set `SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and
`CORS_ORIGINS` as needed. Change `SECRET_KEY` from its development default
before deployment.

## Tests

```bash
python -m unittest discover -s tests
python -m pytest
python -m pytest --cov=tourist_routes --cov-report=term-missing
```

The test suite includes `unittest` and `pytest`-style tests.
