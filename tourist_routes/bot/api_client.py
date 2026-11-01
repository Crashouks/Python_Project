"""Клієнт власного REST API (маршрути). Єдине місце, де бот спілкується з мережею."""
from typing import Optional

import httpx


class ApiError(Exception):
    """API повернуло помилку або відповідь у неочікуваному форматі."""


class ApiUnavailableError(ApiError):
    """Сервіс недоступний: немає з'єднання або вичерпано час очікування."""


class ApiNotFoundError(ApiError):
    """Запитаного ресурсу не існує (HTTP 404)."""


REQUIRED_ROUTE_FIELDS = ("id", "type", "name", "country", "start_city", "length_km")


class RoutesApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0, transport=None):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout, transport=transport)

    async def close(self):
        await self._client.aclose()

    async def _get(self, path: str, params: Optional[dict] = None):
        try:
            response = await self._client.get(path, params=params)
        except httpx.TimeoutException:
            raise ApiUnavailableError("Сервіс не відповів вчасно.") from None
        except httpx.RequestError:
            raise ApiUnavailableError("Не вдалося з'єднатися із сервісом.") from None
        if response.status_code == 404:
            raise ApiNotFoundError(path)
        if response.status_code >= 400:
            raise ApiError(f"Сервіс повернув код {response.status_code}.")
        try:
            return response.json()
        except ValueError:
            raise ApiError("Відповідь сервісу не є коректним JSON.") from None

    @staticmethod
    def _check_route(item) -> dict:
        if not isinstance(item, dict) or any(field not in item for field in REQUIRED_ROUTE_FIELDS):
            raise ApiError("У відповіді сервісу бракує потрібних даних про маршрут.")
        return item

    async def list_routes(self, name=None, country=None, route_type=None, limit=50) -> list:
        params = {"name": name, "country": country, "type": route_type, "limit": limit}
        data = await self._get("/routes", {k: v for k, v in params.items() if v is not None})
        if not isinstance(data, list):
            raise ApiError("Очікувався список маршрутів.")
        return [self._check_route(item) for item in data]

    async def get_route(self, route_id: int) -> dict:
        return self._check_route(await self._get(f"/routes/{int(route_id)}"))
