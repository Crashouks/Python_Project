import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tourist_routes.core import validators  # noqa: E402
from tourist_routes.core.exceptions import RouteNotFoundError, StorageError, ValidationError  # noqa: E402
from tourist_routes.core.factory import get_route_class, list_route_classes, route_from_dict  # noqa: E402
from tourist_routes.core.manager import RouteManager  # noqa: E402
from tourist_routes.core.models import BusTour, CyclingRoute, HikingRoute, Route  # noqa: E402
from tourist_routes.core.route_statistics import RouteStatistics  # noqa: E402
from tourist_routes.core.sample_data import create_sample_routes  # noqa: E402
from tourist_routes.storage.json_storage import JsonStorage  # noqa: E402


class ValidatorsTests(unittest.TestCase):
    def test_text(self):
        self.assertEqual(validators.validate_text("  Привіт ", "Поле"), "Привіт")
        for value, max_len in [("", None), ("   ", None), (5, None), ("abcdef", 3)]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validators.validate_text(value, "Поле", max_len)

    def test_number(self):
        self.assertEqual(validators.validate_number(5, "x", 0, 10), 5)
        for value in (-1, 11, "5", True, float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validators.validate_number(value, "x", 0, 10)

    def test_integer(self):
        self.assertEqual(validators.validate_integer(3, "x", 1, 5), 3)
        for value in (2.5, "3", True, 0, 6):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validators.validate_integer(value, "x", 1, 5)

    def test_choice(self):
        self.assertEqual(validators.validate_choice(" Легкий ", "x", ("легкий", "складний")), "легкий")
        with self.assertRaises(ValidationError):
            validators.validate_choice("інший", "x", ("легкий",))

    def test_rating_and_ratings(self):
        self.assertEqual(validators.validate_rating(8.0), 8)
        self.assertEqual(validators.validate_rating(8.5), 8.5)
        self.assertEqual(validators.validate_ratings((1, 10)), [1, 10])
        for bad in (0, 11, "9"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    validators.validate_rating(bad)
        with self.assertRaises(ValidationError):
            validators.validate_ratings("9 8")

    def test_location(self):
        self.assertEqual(validators.validate_location([" Україна ", "Львів"]), ("Україна", "Львів"))
        for bad in ("Львів", ["Україна"], ["Україна", ""], [1, 2]):
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    validators.validate_location(bad)

    def test_parse_number_and_ratings(self):
        self.assertEqual(validators.parse_number(" 3,5 ", "x"), 3.5)
        self.assertEqual(validators.parse_number("7", "x", int), 7)
        with self.assertRaises(ValidationError):
            validators.parse_number("abc", "x")
        self.assertEqual(validators.parse_ratings("9 8,5 10"), [9, 8.5, 10])
        with self.assertRaises(ValidationError):
            validators.parse_ratings("9 20")


class ModelsTests(unittest.TestCase):
    def setUp(self):
        self.sample = create_sample_routes()

    def test_route_basics(self):
        route = Route("Тест", [8, 10], "Україна", "Київ", 10, "Опис")
        self.assertEqual(route.name, "Тест")
        self.assertEqual((route.country, route.start_city), ("Україна", "Київ"))
        self.assertEqual(route.average_rating(), 9)
        self.assertEqual(route.estimated_duration_hours(), 2)
        self.assertIn("Тест", str(route))
        self.assertEqual(route.extra_details(), [])

    def test_no_ratings_average_is_none(self):
        self.assertIsNone(Route("Тест", [], "Україна", "Київ", 10, "Опис").average_rating())

    def test_add_rating(self):
        route = Route("Тест", [5], "Україна", "Київ", 10, "Опис")
        route.add_rating(9)
        self.assertEqual(route.ratings, [5, 9])
        with self.assertRaises(ValidationError):
            route.add_rating(11)

    def test_ratings_getter_returns_copy(self):
        route = Route("Тест", [5], "Україна", "Київ", 10, "Опис")
        route.ratings.append(10)
        self.assertEqual(route.ratings, [5])

    def test_setters_validate(self):
        route = Route("Тест", [5], "Україна", "Київ", 10, "Опис")
        with self.assertRaises(ValidationError):
            route.name = ""
        with self.assertRaises(ValidationError):
            route.length_km = -1
        with self.assertRaises(ValidationError):
            route.description = " "
        with self.assertRaises(ValidationError):
            route.location = ("Тільки країна",)
        route.name = "Нова"
        route.length_km = 12.5
        route.description = "Новий опис"
        route.location = ("Польща", "Краків")
        self.assertEqual((route.name, route.length_km, route.country), ("Нова", 12.5, "Польща"))

    def test_durations_by_type(self):
        hiking, _, urban, mountain, bus, walk = self.sample[0], None, self.sample[2], self.sample[3], self.sample[4], self.sample[5]
        self.assertAlmostEqual(hiking.estimated_duration_hours(), 45 / 4 + 1800 / 600)
        self.assertAlmostEqual(urban.estimated_duration_hours(), 320 / 15)
        self.assertAlmostEqual(mountain.estimated_duration_hours(), 85 / 10)
        self.assertAlmostEqual(bus.estimated_duration_hours(), 170 / 40 + 8 * 0.25)
        self.assertAlmostEqual(walk.estimated_duration_hours(), 1)

    def test_subclass_validation(self):
        with self.assertRaises(ValidationError):
            HikingRoute("Т", [9], "У", "К", 10, "О", "неможливий", 100)
        with self.assertRaises(ValidationError):
            HikingRoute("Т", [9], "У", "К", 10, "О", "легкий", -5)
        with self.assertRaises(ValidationError):
            CyclingRoute("Т", [9], "У", "К", 10, "О", "багато")
        with self.assertRaises(ValidationError):
            BusTour("Т", [9], "У", "К", 10, "О", 0)

    def test_extra_details(self):
        self.assertEqual(self.sample[0].extra_details(), [("Складність", "середній"), ("Набір висоти (м)", 1800)])
        self.assertEqual(self.sample[4].extra_details(), [("Кількість зупинок", 8)])

    def test_to_dict_from_dict_roundtrip(self):
        for route in self.sample:
            with self.subTest(route=route.name):
                data = route.to_dict()
                self.assertEqual(data["type"], route.__class__.__name__)
                rebuilt = route.__class__.from_dict(data)
                self.assertEqual(rebuilt.to_dict(), data)


class FactoryTests(unittest.TestCase):
    def test_classes(self):
        self.assertEqual({c.__name__ for c in list_route_classes()},
                         {"Route", "HikingRoute", "CyclingRoute", "BusTour"})
        self.assertIs(get_route_class("BusTour"), BusTour)

    def test_unknown_type(self):
        for value in ("Plane", None, 5):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    get_route_class(value)

    def test_route_from_dict_errors(self):
        good = create_sample_routes()[0].to_dict()
        self.assertIsInstance(route_from_dict(good), HikingRoute)
        bad_cases = {
            "not dict": [1],
            "unknown type": dict(good, type="Nope"),
            "missing field": {k: v for k, v in good.items() if k != "difficulty"},
            "bad value": dict(good, length_km="багато"),
            "bad rating": dict(good, ratings=[99]),
        }
        for label, data in bad_cases.items():
            with self.subTest(case=label):
                with self.assertRaises(ValidationError):
                    route_from_dict(data)


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = RouteManager()
        self.ids = [self.manager.add(r) for r in create_sample_routes()]

    def test_add_get_len(self):
        self.assertEqual(len(self.manager), 6)
        self.assertEqual(self.ids, [1, 2, 3, 4, 5, 6])
        self.assertEqual(self.manager.get(1).name, "Карпатська мандрівка")

    def test_get_missing_raises(self):
        with self.assertRaises(RouteNotFoundError):
            self.manager.get(999)

    def test_add_wrong_type(self):
        with self.assertRaises(ValidationError):
            self.manager.add("не маршрут")

    def test_replace_and_remove(self):
        new_route = Route("Нова", [7], "Польща", "Краків", 3, "Опис")
        self.manager.replace(2, new_route)
        self.assertIs(self.manager.get(2), new_route)
        with self.assertRaises(RouteNotFoundError):
            self.manager.replace(99, new_route)
        removed = self.manager.remove(2)
        self.assertIs(removed, new_route)
        with self.assertRaises(RouteNotFoundError):
            self.manager.get(2)
        self.assertEqual(self.manager.add(new_route), 7)

    def test_replace_all(self):
        self.manager.replace_all([Route("А", [], "У", "К", 1, "О")])
        self.assertEqual([i for i, _ in self.manager.all()], [1])
        with self.assertRaises(ValidationError):
            self.manager.replace_all([1])
        self.assertEqual(len(self.manager.routes()), 1)

    def test_search(self):
        self.assertEqual([i for i, _ in self.manager.find_by_name(" КАРПАТ ")], [1])
        self.assertEqual([i for i, _ in self.manager.find_by_country("україна")], [1, 6])
        self.assertEqual(self.manager.find_by_name("немає"), [])

    def test_filters(self):
        self.assertEqual([i for i, _ in self.manager.filter_by_type(CyclingRoute)], [3, 4])
        self.assertEqual([i for i, _ in self.manager.filter_by_length(40, 100)], [1, 2, 4])
        self.assertEqual([i for i, _ in self.manager.filter_by_rating(9.5)], [2])
        self.manager.add(Route("Без відгуків", [], "У", "К", 1, "О"))
        self.assertNotIn(7, [i for i, _ in self.manager.filter_by_rating(0)])

    def test_sorting(self):
        self.assertEqual(self.manager.sort_by_rating()[0][0], 2)
        self.assertEqual([i for i, _ in self.manager.sort_by_length()][:2], [6, 2])
        self.assertEqual(self.manager.sort_by_duration()[0][0], 6)

    def test_statistics(self):
        stats = self.manager.statistics()
        self.assertEqual(stats["total"], 6)
        self.assertEqual(RouteManager().statistics(), None)


class StatisticsTests(unittest.TestCase):
    def test_values(self):
        pairs = list(enumerate(create_sample_routes(), start=1))
        stats = RouteStatistics(pairs)
        self.assertEqual(stats.total(), 6)
        self.assertAlmostEqual(stats.average_length(), (45 + 43 + 320 + 85 + 170 + 5) / 6)
        self.assertEqual(stats.longest()[0], 3)
        self.assertEqual(stats.shortest()[0], 6)
        summary = stats.summary()
        self.assertEqual(summary["ratings"]["max"], 10)
        self.assertEqual(summary["ratings"]["min"], 8)
        self.assertEqual(summary["ratings"]["best"][0], 2)
        self.assertEqual(summary["by_country"]["Україна"], 2)
        self.assertEqual(sum(summary["by_type"].values()), 6)

    def test_no_ratings(self):
        stats = RouteStatistics([(1, Route("А", [], "У", "К", 1, "О"))])
        self.assertIsNone(stats.rating_summary())

    def test_empty(self):
        self.assertIsNone(RouteStatistics([]).summary())


class JsonStorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "data" / "routes.json")
        self.storage = JsonStorage(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_filename_property(self):
        self.assertEqual(self.storage.filename, self.path)
        self.assertTrue(JsonStorage().filename.endswith("routes.json"))

    def test_roundtrip(self):
        routes = create_sample_routes()
        self.storage.save(routes)
        self.assertEqual([r.to_dict() for r in self.storage.load()], [r.to_dict() for r in routes])
        self.assertFalse(Path(self.path + ".tmp").exists())

    def test_load_missing_file_returns_empty_list(self):
        self.assertEqual(self.storage.load(), [])

    def test_load_corrupted_and_invalid(self):
        Path(self.path).parent.mkdir(parents=True)
        cases = {
            "broken": "{oops",
            "not list": '{"a": 1}',
            "bad item": json.dumps([{"type": "Route", "name": ""}]),
        }
        for label, content in cases.items():
            with self.subTest(case=label):
                Path(self.path).write_text(content, encoding="utf-8")
                with self.assertRaises(StorageError):
                    self.storage.load()

    def test_load_os_error_with_mock(self):
        with mock.patch("builtins.open", side_effect=PermissionError("denied")):
            with self.assertRaises(StorageError):
                self.storage.load()

    def test_save_os_error_with_mock_cleans_temp_file(self):
        with mock.patch("builtins.open", side_effect=OSError("disk full")), \
                mock.patch("os.remove") as remove:
            with self.assertRaises(StorageError):
                self.storage.save(create_sample_routes())
        remove.assert_called_once_with(self.path + ".tmp")


if __name__ == "__main__":
    unittest.main()
