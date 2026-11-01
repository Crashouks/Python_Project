"""Обробники команд, текстових повідомлень і натискань кнопок."""
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from tourist_routes.bot import config, formatting, keyboards
from tourist_routes.bot.api_client import ApiError, ApiNotFoundError, ApiUnavailableError

logger = logging.getLogger(__name__)

WELCOME = (
    "Привіт, {name}! 👋\n"
    "Я допоможу знайти туристичний маршрут: перегляд каталогу, пошук, топ за оцінкою "
    "та власне обране.\n\nОберіть дію або введіть /help."
)
HELP_TEXT = (
    "<b>Команди</b>\n"
    "/start — привітання й меню\n"
    "/routes — каталог маршрутів\n"
    "/search назва — пошук за назвою (наприклад: /search карпат)\n"
    "/types — маршрути за типом\n"
    "/top — найвище оцінені маршрути\n"
    "/favorites — моє обране\n"
    "/help — ця підказка\n\n"
    "Також можна просто написати назву маршруту — я його знайду."
)


# ---------- допоміжні функції ----------

def _api(context: ContextTypes.DEFAULT_TYPE):
    return context.bot_data["api"]


def _storage(context: ContextTypes.DEFAULT_TYPE):
    return context.bot_data["storage"]


async def _send(update: Update, text: str, markup=None):
    """Відповідає новим повідомленням або редагує поточне (якщо це натискання кнопки)."""
    query = update.callback_query
    if query is not None:
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)
        except BadRequest as error:
            if "not modified" not in str(error).lower():
                raise
    elif update.effective_message is not None:
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)


async def _fetch(update: Update, call):
    """Виконує запит до API. У разі помилки показує зрозуміле повідомлення й повертає None."""
    try:
        return await call
    except ApiUnavailableError:
        await _send(update, "⚠️ Сервіс маршрутів тимчасово недоступний. Спробуйте трохи пізніше.",
                    keyboards.main_menu())
    except ApiNotFoundError:
        await _send(update, "Маршрут не знайдено — можливо, його вже видалили.", keyboards.main_menu())
    except ApiError as error:
        logger.warning("Помилка API: %s", error)
        await _send(update, "⚠️ Сервіс повернув неочікувану відповідь. Спробуйте пізніше.",
                    keyboards.main_menu())
    return None


async def _show_routes(update: Update, title: str, routes: list):
    if not routes:
        await _send(update, "Нічого не знайдено. Спробуйте інший запит або /routes.", keyboards.main_menu())
        return
    limit = config.MAX_LIST_ITEMS
    await _send(update, formatting.format_route_list(title, routes, limit),
                keyboards.route_list(routes, limit))


# ---------- сценарії (використовуються і командами, і кнопками) ----------

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update, "Оберіть дію:", keyboards.main_menu())


async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    routes = await _fetch(update, _api(context).list_routes(limit=config.FETCH_LIMIT))
    if routes is not None:
        await _show_routes(update, "Каталог маршрутів", routes)


async def show_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update, "Оберіть тип маршруту:", keyboards.types_menu())


async def show_by_type(update: Update, context: ContextTypes.DEFAULT_TYPE, route_type: str):
    routes = await _fetch(update, _api(context).list_routes(route_type=route_type, limit=config.FETCH_LIMIT))
    if routes is not None:
        await _show_routes(update, f"Тип: {formatting.type_label(route_type)}", routes)


async def show_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    routes = await _fetch(update, _api(context).list_routes(limit=200))
    if routes is None:
        return
    rated = [r for r in routes if r.get("average_rating") is not None]
    rated.sort(key=lambda r: r["average_rating"], reverse=True)
    await _show_routes(update, "Найвище оцінені маршрути", rated[:config.TOP_COUNT])


async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ids = set(_storage(context).list_ids(update.effective_user.id))
    if not ids:
        await _send(update, "В обраному поки порожньо. Відкрийте маршрут і натисніть «⭐ В обране».",
                    keyboards.main_menu())
        return
    routes = await _fetch(update, _api(context).list_routes(limit=200))
    if routes is None:
        return
    await _show_routes(update, "Моє обране", [r for r in routes if r["id"] in ids])


async def show_route(update: Update, context: ContextTypes.DEFAULT_TYPE, route_id: int):
    route = await _fetch(update, _api(context).get_route(route_id))
    if route is None:
        return
    is_favorite = _storage(context).is_favorite(update.effective_user.id, route_id)
    await _send(update, formatting.format_route_card(route), keyboards.route_details(route_id, is_favorite))


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    text = text.strip()
    if len(text) < 2:
        await _send(update, "Введіть хоча б 2 символи для пошуку, наприклад: /search карпат")
        return
    routes = await _fetch(update, _api(context).list_routes(name=text, limit=config.FETCH_LIMIT))
    if routes is None:
        return
    if not routes:
        await _send(update, f"За запитом «{formatting.escape(text)}» нічого не знайдено. Спробуйте /routes.",
                    keyboards.main_menu())
        return
    await _show_routes(update, f"Результати пошуку: {text}", routes)


# ---------- обробники Telegram ----------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = formatting.escape(update.effective_user.first_name or "мандрівнику")
    await _send(update, WELCOME.format(name=name), keyboards.main_menu())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update, HELP_TEXT)


async def routes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_all(update, context)


async def types_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_types(update, context)


async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_top(update, context)


async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_favorites(update, context)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await search(update, context, " ".join(context.args or []))


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Звичайний текст сприймаємо як пошуковий запит."""
    await search(update, context, update.effective_message.text or "")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update, "Не знаю такої команди. Ось що я вмію:\n\n" + HELP_TEXT)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = (query.data or "").split(":")
    action = parts[0]

    if action == "menu":
        await show_menu(update, context)
    elif action == "list" and len(parts) == 2 and parts[1] in ("all", "top", "fav"):
        await {"all": show_all, "top": show_top, "fav": show_favorites}[parts[1]](update, context)
    elif action == "types":
        await show_types(update, context)
    elif action == "type" and len(parts) == 2 and parts[1] in keyboards.VALID_ROUTE_TYPES:
        await show_by_type(update, context, parts[1])
    elif action == "route" and len(parts) == 2 and parts[1].isdigit():
        await show_route(update, context, int(parts[1]))
    elif action == "fav" and len(parts) == 3 and parts[1] in ("add", "del") and parts[2].isdigit():
        route_id = int(parts[2])
        user_id = update.effective_user.id
        if parts[1] == "add":
            _storage(context).add(user_id, route_id)
        else:
            _storage(context).remove(user_id, route_id)
        await show_route(update, context, route_id)
    else:
        await _send(update, "Невідома дія. Скористайтеся меню або /help.", keyboards.main_menu())


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Остання лінія захисту: бот не падає, користувач отримує повідомлення."""
    logger.exception("Необроблена помилка", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message is not None:
        try:
            await update.effective_message.reply_text("Сталася внутрішня помилка. Спробуйте ще раз пізніше.")
        except Exception:  # noqa: BLE001
            logger.exception("Не вдалося надіслати повідомлення про помилку")
