import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_BASE_URL = os.getenv("ROUTES_API_URL", "http://127.0.0.1:8000")
API_TIMEOUT_SECONDS = float(os.getenv("ROUTES_API_TIMEOUT", "10"))
BOT_DB_FILE = os.getenv("BOT_DB_FILE", str(PROJECT_ROOT / "data" / "bot.db"))

MAX_LIST_ITEMS = 10      # скільки маршрутів показувати в одному списку
FETCH_LIMIT = 50         # скільки маршрутів просити в API за один запит
TOP_COUNT = 5
