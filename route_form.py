from config import MAX_DESCRIPTION_LENGTH, MAX_LENGTH_KM, MAX_NAME_LENGTH, MIN_LENGTH_KM


class RouteForm:
    def __init__(self, reader):
        self._reader = reader

    def build(self, route_class, existing=None):
        current = existing.to_dict() if existing is not None else {}
        country, start_city = current.get("location", (None, None))

        arguments = {
            "name": self._reader.read_text("Назва маршруту", current.get("name"), MAX_NAME_LENGTH),
            "country": self._reader.read_text("Країна", country, MAX_NAME_LENGTH),
            "start_city": self._reader.read_text("Місто старту", start_city, MAX_NAME_LENGTH),
            "length_km": self._reader.read_number(
                "Протяжність (км)", float, current.get("length_km"), MIN_LENGTH_KM, MAX_LENGTH_KM
            ),
            "ratings": self._reader.read_ratings(current.get("ratings")),
            "description": self._reader.read_text(
                "Опис маршруту", current.get("description"), MAX_DESCRIPTION_LENGTH
            ),
        }
        for field in route_class.extra_fields:
            arguments[field.attribute] = self._reader.read_extra_field(
                field, current.get(field.attribute)
            )
        return route_class(**arguments)
