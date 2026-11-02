"""Ті самі тести math_utils, переписані на pytest (для порівняння з unittest).

Запуск: python -m pytest tests/pytest_style -v
"""
import pytest

from tourist_routes.utils.math_utils import add, divide, factorial, is_even


@pytest.mark.parametrize("a, b, expected", [(2, 3, 5), (-2, -3, -5), (0, 7, 7), (1.5, 2.5, 4.0)])
def test_add(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize("a, b", [("1", 2), (None, 1), (True, 1)])
def test_add_invalid_types(a, b):
    with pytest.raises(TypeError):
        add(a, b)


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)


@pytest.mark.parametrize("n, expected", [(0, True), (2, True), (-4, True), (1, False), (99, False)])
def test_is_even(n, expected):
    assert is_even(n) is expected


@pytest.mark.parametrize("value", [2.5, "2", None, True])
def test_is_even_invalid(value):
    with pytest.raises(TypeError):
        is_even(value)


@pytest.mark.parametrize("n, expected", [(0, 1), (1, 1), (5, 120), (10, 3628800)])
def test_factorial(n, expected):
    assert factorial(n) == expected


def test_factorial_negative():
    with pytest.raises(ValueError):
        factorial(-1)


@pytest.mark.parametrize("value", [3.5, "5", None])
def test_factorial_invalid_type(value):
    with pytest.raises(TypeError):
        factorial(value)
