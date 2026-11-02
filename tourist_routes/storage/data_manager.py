"""Робота з JSON-файлами: читання/запис користувачів, вибірка за віком, обмін маршрутами.

Це узагальнення JSON-сховища: ті самі принципи (читання, перевірка даних, запис,
обробка помилок), що й у JsonStorage, але для довільного списку записів.
"""
import json
import os

from tourist_routes.core.exceptions import StorageError
from tourist_routes.storage.json_storage import JsonStorage


def _validate_user(user, index):
    if not isinstance(user, dict):
        raise StorageError(f"Запис №{index} має бути об'єктом JSON.")
    name, age = user.get("name"), user.get("age")
    if not isinstance(name, str) or not name.strip():
        raise StorageError(f"Запис №{index}: поле 'name' має бути непорожнім рядком.")
    if isinstance(age, bool) or not isinstance(age, int) or age < 0:
        raise StorageError(f"Запис №{index}: поле 'age' має бути невід'ємним цілим числом.")
    return user


def load_users(path):
    """Зчитує список користувачів [{'name': ..., 'age': ...}, ...] з JSON-файлу."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise StorageError(f"Файл {path} не знайдено.") from None
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise StorageError(f"Файл {path} пошкоджено: {error}") from error
    except OSError as error:
        raise StorageError(f"Не вдалося прочитати файл {path}: {error}") from error
    if not isinstance(data, list):
        raise StorageError(f"Файл {path} має містити список.")
    return [_validate_user(user, index) for index, user in enumerate(data, start=1)]


def save_users(path, users):
    """Зберігає список користувачів у JSON-файл."""
    for index, user in enumerate(users, start=1):
        _validate_user(user, index)
    try:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(json.dumps(list(users), ensure_ascii=False, indent=4))
    except OSError as error:
        raise StorageError(f"Не вдалося записати файл {path}: {error}") from error


def filter_older_than(users, min_age):
    """Повертає користувачів, старших за min_age (суворо більше)."""
    if isinstance(min_age, bool) or not isinstance(min_age, (int, float)):
        raise TypeError("Вік має бути числом.")
    return [user for user in users if user["age"] > min_age]


def get_users_older_than(path, min_age):
    """Зчитує файл і повертає користувачів старших за вказаний вік."""
    return filter_older_than(load_users(path), min_age)


def load_routes(path):
    """Зчитує маршрути з JSON (через JsonStorage)."""
    return JsonStorage(path).load()


def save_routes(path, routes):
    """Зберігає маршрути у JSON (через JsonStorage)."""
    JsonStorage(path).save(routes)
