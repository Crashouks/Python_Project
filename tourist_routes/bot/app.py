"""Збирання й запуск Telegram-бота."""
import logging
import sys

from telegram import BotCommand
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from tourist_routes.bot import config, handlers
from tourist_routes.bot.api_client import RoutesApiClient
from tourist_routes.bot.storage import FavoritesStorage

COMMANDS = [
    BotCommand("start", "Привітання й меню"),
    BotCommand("routes", "Каталог маршрутів"),
    BotCommand("search", "Пошук за назвою"),
    BotCommand("types", "Маршрути за типом"),
    BotCommand("top", "Найвище оцінені"),
    BotCommand("favorites", "Моє обране"),
    BotCommand("help", "Допомога"),
]


async def _post_init(application: Application):
    await application.bot.set_my_commands(COMMANDS)


async def _post_shutdown(application: Application):
    await application.bot_data["api"].close()


def build_application(token: str, api_client=None, storage=None) -> Application:
    application = (
        Application.builder().token(token).post_init(_post_init).post_shutdown(_post_shutdown).build()
    )
    application.bot_data["api"] = api_client or RoutesApiClient(
        config.API_BASE_URL, timeout=config.API_TIMEOUT_SECONDS
    )
    application.bot_data["storage"] = storage or FavoritesStorage(config.BOT_DB_FILE)

    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("routes", handlers.routes_command))
    application.add_handler(CommandHandler("search", handlers.search_command))
    application.add_handler(CommandHandler("types", handlers.types_command))
    application.add_handler(CommandHandler("top", handlers.top_command))
    application.add_handler(CommandHandler("favorites", handlers.favorites_command))
    application.add_handler(CallbackQueryHandler(handlers.button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_message))
    application.add_handler(MessageHandler(filters.COMMAND, handlers.unknown_command))
    application.add_error_handler(handlers.error_handler)
    return application


def main():
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
    # httpx на рівні INFO друкує повні URL запитів, а в них є токен бота.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    if not config.BOT_TOKEN:
        print("Не задано токен бота. Встановіть змінну середовища TELEGRAM_BOT_TOKEN "
              "(токен видає @BotFather у Telegram).")
        sys.exit(1)
    build_application(config.BOT_TOKEN).run_polling()
