import math

from config import MAX_NAME_LENGTH, MAX_RATING, MIN_RATING
from exceptions import ValidationError


def validate_text(value, field_name, max_length=None):
    if not isinstance(value, str):
        raise ValidationError(f"{field_name}: потрібен текст.")
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field_name}: поле не може бути порожнім.")
    if max_length is not None and len(cleaned) > max_length:
        raise ValidationError(f"{field_name}: максимум {max_length} символів.")
    return cleaned


def validate_number(value, field_name, min_value=None, max_value=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field_name}: потрібне числове значення.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValidationError(f"{field_name}: потрібне скінченне число.")
    if min_value is not None and value < min_value:
        raise ValidationError(f"{field_name}: значення не може бути меншим за {min_value:g}.")
    if max_value is not None and value > max_value:
        raise ValidationError(f"{field_name}: значення не може бути більшим за {max_value:g}.")
    return value


def validate_integer(value, field_name, min_value=None, max_value=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{field_name}: потрібне ціле число.")
    return validate_number(value, field_name, min_value, max_value)


def validate_choice(value, field_name, choices):
    cleaned = validate_text(value, field_name).lower()
    if cleaned not in choices:
        raise ValidationError(f"{field_name}: оберіть одне зі значень ({', '.join(choices)}).")
    return cleaned


def validate_rating(value):
    checked = validate_number(value, "Бал", MIN_RATING, MAX_RATING)
    return int(checked) if isinstance(checked, float) and checked.is_integer() else checked


def validate_ratings(values):
    if not isinstance(values, (list, tuple)):
        raise ValidationError("Відгуки: потрібен список балів.")
    return [validate_rating(value) for value in values]


def validate_location(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValidationError("Локація: потрібна пара (країна, місто старту).")
    country, start_city = value
    return (
        validate_text(country, "Країна", MAX_NAME_LENGTH),
        validate_text(start_city, "Місто старту", MAX_NAME_LENGTH),
    )


def parse_number(raw, field_name, number_type=float):
    try:
        return number_type(raw.strip().replace(",", "."))
    except ValueError:
        raise ValidationError(f"{field_name}: введіть коректне число.") from None


def parse_ratings(raw):
    return validate_ratings([parse_number(part, "Бал") for part in raw.split()])
