class RouteError(Exception):
    pass


class ValidationError(RouteError, ValueError):
    pass


class RouteNotFoundError(RouteError):
    pass


class StorageError(RouteError):
    pass
