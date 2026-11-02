import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tourist_routes.utils.math_utils import add, divide, factorial, is_even  # noqa: E402


class AddTests(unittest.TestCase):
    def test_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_negative_and_zero(self):
        self.assertEqual(add(-2, -3), -5)
        self.assertEqual(add(0, 7), 7)

    def test_floats(self):
        self.assertAlmostEqual(add(0.1, 0.2), 0.3)

    def test_invalid_types(self):
        for a, b in [("1", 2), (None, 1), (True, 1), ([1], 2)]:
            with self.subTest(a=a, b=b):
                with self.assertRaises(TypeError):
                    add(a, b)


class DivideTests(unittest.TestCase):
    def test_regular_division(self):
        self.assertEqual(divide(10, 4), 2.5)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            divide(1, 0)

    def test_zero_numerator(self):
        self.assertEqual(divide(0, 5), 0)

    def test_invalid_types(self):
        with self.assertRaises(TypeError):
            divide("1", 2)


class IsEvenTests(unittest.TestCase):
    def test_even_numbers(self):
        for n in (0, 2, 100, -4):
            with self.subTest(n=n):
                self.assertTrue(is_even(n))

    def test_odd_numbers(self):
        for n in (1, 7, -3, 99):
            with self.subTest(n=n):
                self.assertFalse(is_even(n))

    def test_zero_is_even(self):
        self.assertIs(is_even(0), True)

    def test_non_integer_raises(self):
        for value in (2.5, "2", None, True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    is_even(value)


class FactorialTests(unittest.TestCase):
    def test_known_values(self):
        for n, expected in [(0, 1), (1, 1), (5, 120), (10, 3628800)]:
            with self.subTest(n=n):
                self.assertEqual(factorial(n), expected)

    def test_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            factorial(-1)

    def test_non_integer_raises_type_error(self):
        for value in (3.5, "5", None, True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    factorial(value)

    def test_grows_correctly(self):
        self.assertEqual(factorial(6), 6 * factorial(5))


if __name__ == "__main__":
    unittest.main()
