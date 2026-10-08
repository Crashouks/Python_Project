from exceptions import ValidationError
from models import BusTour, CyclingRoute, HikingRoute, Route

ROUTE_CLASSES = {
    route_class.__name__: route_class
    for route_class in (Route, HikingRoute, CyclingRoute, BusTour)
}


def list_route_classes():
    return list(ROUTE_CLASSES.values())


def get_route_class(type_name):
    route_class = ROUTE_CLASSES.get(type_name) if isinstance(type_name, str) else None
    if route_class is None:
        raise ValidationError(f"Невідомий тип маршруту: {type_name}.")
    return route_class


def route_from_dict(data):
    if not isinstance(data, dict):
        raise ValidationError("Запис маршруту має бути об'єктом JSON.")
    route_class = get_route_class(data.get("type"))
    try:
        return route_class.from_dict(data)
    except KeyError as error:
        raise ValidationError(f"Відсутнє обов'язкове поле {error}.") from None
    except (TypeError, ValueError) as error:
        raise ValidationError(f"Некоректні дані маршруту: {error}") from None
