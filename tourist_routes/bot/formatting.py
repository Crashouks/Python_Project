"""Чисті функції форматування тексту відповідей (без залежності від Telegram)."""
from html import escape

from tourist_routes.core.exceptions import ValidationError
from tourist_routes.core.factory import get_route_class

EXTRA_LABELS = (
    ("difficulty", "Складність", "{}"),
    ("elevation_gain_m", "Набір висоти", "{:g} м"),
    ("bike_type", "Тип велосипеда", "{}"),
    ("stops_count", "Зупинок", "{}"),
)


def type_label(type_name: str) -> str:
    try:
        return get_route_class(type_name).type_name
    except ValidationError:
        return str(type_name)


def format_duration(hours) -> str:
    total_minutes = round(float(hours) * 60)
    hours_part, minutes_part = divmod(total_minutes, 60)
    if hours_part and minutes_part:
        return f"{hours_part} год {minutes_part} хв"
    if hours_part:
        return f"{hours_part} год"
    return f"{minutes_part} хв"


def format_rating(route: dict) -> str:
    average = route.get("average_rating")
    if average is None:
        return "немає відгуків"
    count = len(route.get("ratings") or [])
    return f"⭐ {average:.1f} (відгуків: {count})"


def format_route_card(route: dict) -> str:
    lines = [
        f"<b>{escape(str(route['name']))}</b>",
        f"Тип: {escape(type_label(route['type']))}",
        f"Країна: {escape(str(route['country']))}, старт: {escape(str(route['start_city']))}",
        f"Протяжність: {route['length_km']:g} км",
    ]
    if route.get("estimated_duration_hours") is not None:
        lines.append(f"Орієнтовна тривалість: {format_duration(route['estimated_duration_hours'])}")
    lines.append(f"Оцінка: {format_rating(route)}")
    for key, label, template in EXTRA_LABELS:
        value = route.get(key)
        if value is not None:
            lines.append(f"{label}: {escape(template.format(value))}")
    if route.get("description"):
        lines.append("")
        lines.append(escape(str(route["description"])))
    return "\n".join(lines)


def format_route_list(title: str, routes: list, shown_limit: int) -> str:
    lines = [f"<b>{escape(title)}</b>"]
    for index, route in enumerate(routes[:shown_limit], start=1):
        rating = route.get("average_rating")
        rating_text = f", ⭐ {rating:.1f}" if rating is not None else ""
        lines.append(
            f"{index}. {escape(str(route['name']))} — {escape(str(route['country']))}, "
            f"{route['length_km']:g} км{rating_text}"
        )
    if len(routes) > shown_limit:
        lines.append(f"\nПоказано перші {shown_limit} із {len(routes)}. Уточніть пошук: /search назва")
    lines.append("\nОберіть маршрут кнопкою нижче.")
    return "\n".join(lines)
