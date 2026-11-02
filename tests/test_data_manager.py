import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tourist_routes.core.exceptions import StorageError  # noqa: E402
from tourist_routes.core.sample_data import create_sample_routes  # noqa: E402
from tourist_routes.storage import data_manager  # noqa: E402

USERS = [
    {"name": "Олена", "age": 17},
    {"name": "Іван", "age": 18},
    {"name": "Марія", "age": 30},
    {"name": "Петро", "age": 65},
]
USERS_JSON = json.dumps(USERS, ensure_ascii=False)


class LoadUsersTests(unittest.TestCase):
    def test_load_reads_file_via_mock(self):
        with mock.patch("builtins.open", mock.mock_open(read_data=USERS_JSON)) as mocked_open:
            users = data_manager.load_users("users.json")
        mocked_open.assert_called_once_with("users.json", "r", encoding="utf-8")
        self.assertEqual(users, USERS)

    def test_missing_file(self):
        with mock.patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(StorageError):
                data_manager.load_users("nope.json")

    def test_os_error(self):
        with mock.patch("builtins.open", side_effect=PermissionError("denied")):
            with self.assertRaises(StorageError):
                data_manager.load_users("users.json")

    def test_invalid_content(self):
        cases = {
            "broken json": "{not json",
            "not a list": '{"name": "A", "age": 1}',
            "item not object": "[1, 2]",
            "no name": '[{"age": 5}]',
            "empty name": '[{"name": "  ", "age": 5}]',
            "age text": '[{"name": "A", "age": "5"}]',
            "age negative": '[{"name": "A", "age": -1}]',
            "age bool": '[{"name": "A", "age": true}]',
        }
        for label, content in cases.items():
            with self.subTest(case=label):
                with mock.patch("builtins.open", mock.mock_open(read_data=content)):
                    with self.assertRaises(StorageError):
                        data_manager.load_users("users.json")


class FilterTests(unittest.TestCase):
    def test_older_than_parametrized(self):
        cases = [(0, 4), (17, 3), (18, 2), (30, 1), (65, 0), (100, 0), (17.5, 3)]
        for min_age, expected_count in cases:
            with self.subTest(min_age=min_age):
                self.assertEqual(len(data_manager.filter_older_than(USERS, min_age)), expected_count)

    def test_boundary_is_strict(self):
        names = [u["name"] for u in data_manager.filter_older_than(USERS, 18)]
        self.assertNotIn("Іван", names)
        self.assertEqual(names, ["Марія", "Петро"])

    def test_invalid_age_argument(self):
        for value in ("18", None, True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    data_manager.filter_older_than(USERS, value)

    def test_get_users_older_than_uses_load_users_once(self):
        with mock.patch.object(data_manager, "load_users", return_value=USERS) as mocked_load:
            result = data_manager.get_users_older_than("users.json", 29)
        mocked_load.assert_called_once_with("users.json")
        self.assertEqual([u["name"] for u in result], ["Марія", "Петро"])

    def test_get_users_older_than_end_to_end_with_mock_open(self):
        with mock.patch("builtins.open", mock.mock_open(read_data=USERS_JSON)):
            result = data_manager.get_users_older_than("users.json", 60)
        self.assertEqual(result, [USERS[3]])


class SaveUsersTests(unittest.TestCase):
    def test_save_writes_json_via_mock(self):
        handle_factory = mock.mock_open()
        with mock.patch("builtins.open", handle_factory), mock.patch("os.makedirs") as makedirs:
            data_manager.save_users("out/users.json", USERS)
        makedirs.assert_called_once_with("out", exist_ok=True)
        handle_factory.assert_called_once_with("out/users.json", "w", encoding="utf-8")
        handle_factory().write.assert_called_once()
        written = handle_factory().write.call_args.args[0]
        self.assertEqual(json.loads(written), USERS)
        self.assertIn("Олена", written)

    def test_save_without_directory_does_not_create_dirs(self):
        with mock.patch("builtins.open", mock.mock_open()), mock.patch("os.makedirs") as makedirs:
            data_manager.save_users("users.json", USERS)
        makedirs.assert_not_called()

    def test_save_rejects_invalid_user_before_writing(self):
        with mock.patch("builtins.open", mock.mock_open()) as mocked_open:
            with self.assertRaises(StorageError):
                data_manager.save_users("users.json", [{"name": "A"}])
        mocked_open.assert_not_called()

    def test_save_os_error(self):
        with mock.patch("builtins.open", side_effect=OSError("disk full")):
            with self.assertRaises(StorageError):
                data_manager.save_users("users.json", USERS)

    def test_roundtrip_on_real_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "users.json"
            data_manager.save_users(str(path), USERS)
            self.assertEqual(data_manager.load_users(str(path)), USERS)
            self.assertEqual(len(data_manager.get_users_older_than(str(path), 20)), 2)


class RoutesHelpersTests(unittest.TestCase):
    def test_routes_roundtrip(self):
        routes = create_sample_routes()
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "routes.json")
            data_manager.save_routes(path, routes)
            loaded = data_manager.load_routes(path)
        self.assertEqual([r.to_dict() for r in loaded], [r.to_dict() for r in routes])

    def test_load_routes_delegates_to_storage(self):
        with mock.patch.object(data_manager, "JsonStorage") as storage_class:
            storage_class.return_value.load.return_value = ["route"]
            self.assertEqual(data_manager.load_routes("r.json"), ["route"])
        storage_class.assert_called_once_with("r.json")
        storage_class.return_value.load.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
