from config import MAX_RATING, MIN_LENGTH_KM, MIN_RATING


def read_text(prompt, default=None):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        print("Поле не може бути порожнім.")


def read_number(prompt, number_type=float, default=None, min_value=None):
    suffix = f" [{default:g}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip().replace(",", ".")
        if not raw and default is not None:
            return default
        try:
            value = number_type(raw)
        except ValueError:
            print("Введіть коректне число.")
            continue
        if min_value is not None and value < min_value:
            print(f"Значення має бути не менше {min_value}.")
            continue
        return value


def parse_ratings(raw):
    ratings = []
    for part in raw.replace(",", ".").split():
        value = float(part)
        if not MIN_RATING <= value <= MAX_RATING:
            raise ValueError("rating out of range")
        ratings.append(int(value) if value.is_integer() else value)
    return ratings


def build_ratings_prompt(default):
    prompt = f"Введіть відгуки (бали {MIN_RATING}-{MAX_RATING}) через пробіл"
    if default is not None:
        shown = " ".join(f"{rating:g}" for rating in default)
        prompt += f" [{shown}] ('-' щоб очистити)"
    return prompt + ": "


def read_ratings(default=None):
    prompt = build_ratings_prompt(default)
    while True:
        raw = input(prompt).strip()
        if not raw:
            return list(default) if default is not None else []
        if raw == "-":
            return []
        try:
            return parse_ratings(raw)
        except ValueError:
            print(f"Потрібні числа від {MIN_RATING} до {MAX_RATING}, розділені пробілами.")


def read_route_id(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        print("ID має бути числом.\n")
        return None


def read_route_data(existing=None):
    current = existing or {}
    current_country, current_city = current.get("location", (None, None))

    name = read_text("Введіть назву маршруту", current.get("name"))
    country = read_text("Введіть країну", current_country)
    start_city = read_text("Введіть місто старту", current_city)
    length_km = read_number(
        "Введіть протяжність (км)", float, current.get("length_km"), min_value=MIN_LENGTH_KM
    )
    ratings = read_ratings(current.get("ratings"))
    description = read_text("Введіть опис маршруту", current.get("description"))
    return name, ratings, country, start_city, length_km, description
