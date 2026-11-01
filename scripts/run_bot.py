"""Запускає Telegram-бота:  python scripts/run_bot.py  (потрібна змінна TELEGRAM_BOT_TOKEN)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tourist_routes.bot.app import main  # noqa: E402

if __name__ == "__main__":
    main()
