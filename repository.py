routes = {}


def generate_id():
    return max(routes, default=0) + 1


def save_route(route):
    route_id = generate_id()
    routes[route_id] = route
    return route_id


def find_route(route_id):
    return routes.get(route_id)


def replace_route(route_id, route):
    routes[route_id] = route


def remove_route(route_id):
    return routes.pop(route_id, None)


def all_routes():
    return list(routes.items())


def select_routes(predicate):
    return [(route_id, route) for route_id, route in routes.items() if predicate(route)]
