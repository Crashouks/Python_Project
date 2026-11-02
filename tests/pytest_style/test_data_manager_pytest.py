"""Параметризовані pytest-тести для data_manager (mock + tmp_path).

Запуск: python -m pytest tests/pytest_style -v
"""
import json
from unittest import mock

import pytest

from tourist_routes.core.exceptions import StorageError
from tourist_routes.storage import data_manager

USERS = [
    {"name": "Олена", "age": 17},
    {"name": "Іван", "age": 18},
    {"name": "Марія", "age": 30},
    {"name": "Петро", "age": 65},
]


@pytest.mark.parametrize("min_age, expected_names", [
    (0, ["Олена", "Іван", "Марія", "Петро"]),
    (17, ["Іван", "Марія", "Петро"]),
    (18, ["Марія", "Петро"]),
    (64, ["Петро"]),
    (65, []),
])
def test_filter_older_than(min_age, expected_names):
    assert [u["name"] for u in data_manager.filter_older_than(USERS, min_age)] == expected_names


def test_load_users_with_mocked_open():
    data = json.dumps(USERS, ensure_ascii=False)
    with mock.patch("builtins.open", mock.mock_open(read_data=data)) as mocked_open:
        assert data_manager.load_users("users.json") == USERS
    mocked_open.assert_called_once_with("users.json", "r", encoding="utf-8")


@pytest.mark.parametrize("content", [
    "{broken", '{"a": 1}', "[1]", '[{"age": 5}]', '[{"name": "A", "age": "5"}]',
])
def test_load_users_invalid_content(content):
    with mock.patch("builtins.open", mock.mock_open(read_data=content)):
        with pytest.raises(StorageError):
            data_manager.load_users("users.json")


def test_get_users_older_than_calls_loader_once():
    with mock.patch.object(data_manager, "load_users", return_value=USERS) as loader:
        result = data_manager.get_users_older_than("users.json", 29)
    loader.assert_called_once_with("users.json")
    assert [u["name"] for u in result] == ["Марія", "Петро"]


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "nested" / "users.json"
    data_manager.save_users(str(path), USERS)
    assert data_manager.load_users(str(path)) == USERS


def test_save_writes_once_and_creates_directory():
    opener = mock.mock_open()
    with mock.patch("builtins.open", opener), mock.patch("os.makedirs") as makedirs:
        data_manager.save_users("out/users.json", USERS)
    makedirs.assert_called_once_with("out", exist_ok=True)
    opener().write.assert_called_once()
