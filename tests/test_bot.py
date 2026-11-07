import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tourist_routes.bot import formatting  # noqa: E402
from tourist_routes.bot.storage import FavoritesStorage  # noqa: E402

ROUTE = {
    "id": 1, "type": "HikingRoute", "name": "Карпатська <мандрівка>", "country": "Україна",
    "start_city": "Ворохта", "length_km": 45, "description": "Похід через полонини.",
    "ratings": [9, 10, 8], "average_rating": 9.0, "estimated_duration_hours": 14.25,
    "difficulty": "середній", "elevation_gain_m": 1800, "bike_type": None, "stops_count": None,
}


class FormattingTests(unittest.TestCase):
    def test_duration(self):
        self.assertEqual(formatting.format_duration(14.25), "14 год 15 хв")
        self.assertEqual(formatting.format_duration(2), "2 год")
        self.assertEqual(formatting.format_duration(0.5), "30 хв")

    def test_card_contains_data_and_escapes_html(self):
        card = formatting.format_route_card(ROUTE)
        self.assertIn("Карпатська &lt;мандрівка&gt;", card)
        self.assertIn("45 км", card)
        self.assertIn("14 год 15 хв", card)
        self.assertIn("Складність: середній", card)
        self.assertIn("1800 м", card)
        self.assertNotIn("Тип велосипеда", card)

    def test_card_without_ratings(self):
        route = dict(ROUTE, average_rating=None, ratings=[])
        self.assertIn("немає відгуків", formatting.format_route_card(route))

    def test_list_truncates_and_hints(self):
        routes = [dict(ROUTE, id=i) for i in range(1, 15)]
        text = formatting.format_route_list("Каталог", routes, 10)
        self.assertIn("10. ", text)
        self.assertNotIn("11. ", text)
        self.assertIn("із 14", text)

    def test_unknown_type_label_does_not_crash(self):
        self.assertEqual(formatting.type_label("Невідомий"), "Невідомий")


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = FavoritesStorage(Path(self.tmp.name) / "bot.db")

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_remove_list(self):
        self.assertTrue(self.storage.add(1, 10))
        self.assertFalse(self.storage.add(1, 10))
        self.storage.add(1, 11)
        self.storage.add(2, 10)
        self.assertEqual(self.storage.list_ids(1), [10, 11])
        self.assertTrue(self.storage.is_favorite(2, 10))
        self.assertTrue(self.storage.remove(1, 10))
        self.assertFalse(self.storage.remove(1, 10))
        self.assertFalse(self.storage.is_favorite(1, 10))
        self.assertEqual(self.storage.list_ids(3), [])

    def test_data_persists_between_instances(self):
        self.storage.add(5, 7)
        again = FavoritesStorage(self.storage.db_file)
        self.assertEqual(again.list_ids(5), [7])


class ApplicationTests(unittest.TestCase):
    def test_application_registers_bot_commands_and_handlers(self):
        from tourist_routes.bot.app import build_application

        application = build_application(
            "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi",
            api_client=object(),
            storage=object(),
        )

        self.assertIn("api", application.bot_data)
        self.assertIn("storage", application.bot_data)
        registered_commands = {
            command
            for handlers in application.handlers.values()
            for handler in handlers
            for command in getattr(handler, "commands", ())
        }
        self.assertEqual(
            registered_commands,
            {"start", "help", "routes", "search", "types", "top", "favorites"},
        )


@unittest.skipUnless(importlib.util.find_spec("httpx"), "потрібен httpx")
class ApiClientTests(unittest.IsolatedAsyncioTestCase):
    def make_client(self, handler):
        import httpx

        from tourist_routes.bot.api_client import RoutesApiClient

        return RoutesApiClient("http://test", transport=httpx.MockTransport(handler))

    async def test_list_and_get(self):
        import httpx

        def handler(request):
            if request.url.path == "/routes":
                self.assertEqual(request.url.params.get("name"), "карпат")
                return httpx.Response(200, json=[ROUTE])
            if request.url.path == "/routes/1":
                return httpx.Response(200, json=ROUTE)
            return httpx.Response(404)

        client = self.make_client(handler)
        self.assertEqual((await client.list_routes(name="карпат"))[0]["id"], 1)
        self.assertEqual((await client.get_route(1))["name"], ROUTE["name"])
        await client.close()

    async def test_error_cases(self):
        import httpx

        from tourist_routes.bot.api_client import ApiError, ApiNotFoundError, ApiUnavailableError

        async def check(handler, expected):
            client = self.make_client(handler)
            with self.assertRaises(expected):
                await client.get_route(1)
            await client.close()

        await check(lambda r: httpx.Response(404), ApiNotFoundError)
        await check(lambda r: httpx.Response(500), ApiError)
        await check(lambda r: httpx.Response(200, text="не json"), ApiError)
        await check(lambda r: httpx.Response(200, json={"id": 1}), ApiError)

        def unreachable(request):
            raise httpx.ConnectError("down", request=request)

        await check(unreachable, ApiUnavailableError)

        def timeout(request):
            raise httpx.ReadTimeout("slow", request=request)

        await check(timeout, ApiUnavailableError)


if __name__ == "__main__":
    unittest.main()
