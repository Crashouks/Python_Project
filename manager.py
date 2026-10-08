from exceptions import RouteNotFoundError, ValidationError
from models import Route
from route_statistics import RouteStatistics


class RouteManager:
    def __init__(self):
        self._routes = {}

    def __len__(self):
        return len(self._routes)

    @staticmethod
    def _ensure_route(route):
        if not isinstance(route, Route):
            raise ValidationError("Можна зберігати лише об'єкти типу Route.")

    def _next_id(self):
        return max(self._routes, default=0) + 1

    def add(self, route):
        self._ensure_route(route)
        route_id = self._next_id()
        self._routes[route_id] = route
        return route_id

    def get(self, route_id):
        try:
            return self._routes[route_id]
        except KeyError:
            raise RouteNotFoundError(f"Маршрут з ID {route_id} не знайдено.") from None

    def replace(self, route_id, route):
        self.get(route_id)
        self._ensure_route(route)
        self._routes[route_id] = route

    def remove(self, route_id):
        route = self.get(route_id)
        del self._routes[route_id]
        return route

    def replace_all(self, routes):
        new_routes = list(routes)
        for route in new_routes:
            self._ensure_route(route)
        self._routes = {route_id: route for route_id, route in enumerate(new_routes, start=1)}

    def all(self):
        return list(self._routes.items())

    def routes(self):
        return list(self._routes.values())

    def select(self, predicate):
        return [(route_id, route) for route_id, route in self._routes.items() if predicate(route)]

    def find_by_name(self, query):
        query = query.strip().lower()
        return self.select(lambda route: query in route.name.lower())

    def find_by_country(self, query):
        query = query.strip().lower()
        return self.select(lambda route: query in route.country.lower())

    def filter_by_type(self, route_class):
        return self.select(lambda route: route.__class__ is route_class)

    def filter_by_length(self, min_length, max_length):
        return self.select(lambda route: min_length <= route.length_km <= max_length)

    def filter_by_rating(self, min_average):
        def has_min_average(route):
            average = route.average_rating()
            return average is not None and average >= min_average

        return self.select(has_min_average)

    def sorted_by(self, key_func, reverse=False):
        return sorted(self.all(), key=lambda pair: key_func(pair[1]), reverse=reverse)

    def sort_by_rating(self):
        return self.sorted_by(lambda route: route.average_rating() or 0, reverse=True)

    def sort_by_length(self):
        return self.sorted_by(lambda route: route.length_km)

    def sort_by_duration(self):
        return self.sorted_by(lambda route: route.estimated_duration_hours())

    def statistics(self):
        return RouteStatistics(self.all()).summary()
