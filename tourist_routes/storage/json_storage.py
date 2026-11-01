import contextlib
import json
import os

from tourist_routes.core.config import DATA_FILE
from tourist_routes.core.exceptions import StorageError, ValidationError
from tourist_routes.core.factory import route_from_dict


class JsonStorage:
    def __init__(self, filename=DATA_FILE):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def save(self, routes):
        data = [route.to_dict() for route in routes]
        temp_filename = f"{self._filename}.tmp"
        try:
            os.makedirs(os.path.dirname(self._filename) or ".", exist_ok=True)
            with open(temp_filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            os.replace(temp_filename, self._filename)
        except OSError as error:
            with contextlib.suppress(OSError):
                os.remove(temp_filename)
            raise StorageError(f"Не вдалося записати файл {self._filename}: {error}") from error

    def load(self):
        try:
            with open(self._filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as error:
            raise StorageError(f"Файл {self._filename} пошкоджено: {error}") from error
        except OSError as error:
            raise StorageError(f"Не вдалося прочитати файл {self._filename}: {error}") from error

        if not isinstance(data, list):
            raise StorageError(f"Файл {self._filename} має містити список маршрутів.")

        try:
            return [route_from_dict(item) for item in data]
        except ValidationError as error:
            raise StorageError(f"Помилка в даних файлу {self._filename}: {error}") from error
