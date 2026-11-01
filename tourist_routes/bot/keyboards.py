"""Побудова inline-клавіатур. Формат callback_data: дія[:параметр]."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

ROUTE_TYPES = (
    ("Route", "🚶 Прогулянки"),
    ("HikingRoute", "🥾 Пішохідні"),
    ("CyclingRoute", "🚴 Велосипедні"),
    ("BusTour", "🚌 Автобусні"),
)
VALID_ROUTE_TYPES = {code for code, _ in ROUTE_TYPES}
MENU_BUTTON = InlineKeyboardButton("🏠 Меню", callback_data="menu")


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺 Усі маршрути", callback_data="list:all")],
        [InlineKeyboardButton("🧭 За типом", callback_data="types")],
        [InlineKeyboardButton("🏆 Топ за оцінкою", callback_data="list:top")],
        [InlineKeyboardButton("⭐ Моє обране", callback_data="list:fav")],
    ])


def types_menu() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(label, callback_data=f"type:{code}")] for code, label in ROUTE_TYPES]
    rows.append([MENU_BUTTON])
    return InlineKeyboardMarkup(rows)


def route_list(routes: list, shown_limit: int) -> InlineKeyboardMarkup:
    rows = []
    for route in routes[:shown_limit]:
        title = str(route["name"])
        title = title if len(title) <= 40 else title[:37] + "..."
        rows.append([InlineKeyboardButton(title, callback_data=f"route:{route['id']}")])
    rows.append([MENU_BUTTON])
    return InlineKeyboardMarkup(rows)


def route_details(route_id: int, is_favorite: bool) -> InlineKeyboardMarkup:
    if is_favorite:
        favorite_button = InlineKeyboardButton("💔 Прибрати з обраного", callback_data=f"fav:del:{route_id}")
    else:
        favorite_button = InlineKeyboardButton("⭐ В обране", callback_data=f"fav:add:{route_id}")
    return InlineKeyboardMarkup([
        [favorite_button],
        [InlineKeyboardButton("⬅ До списку", callback_data="list:all"), MENU_BUTTON],
    ])
