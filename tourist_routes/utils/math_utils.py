"""Прості математичні функції (використовуються, зокрема, для демонстрації модульного тестування)."""


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def add(a, b):
    """Повертає суму двох чисел."""
    if not (_is_number(a) and _is_number(b)):
        raise TypeError("add() приймає лише числа.")
    return a + b


def divide(a, b):
    """Ділить a на b; при діленні на нуль піднімає ZeroDivisionError із зрозумілим повідомленням."""
    if not (_is_number(a) and _is_number(b)):
        raise TypeError("divide() приймає лише числа.")
    if b == 0:
        raise ZeroDivisionError("Ділення на нуль неможливе.")
    return a / b


def is_even(n):
    """Перевіряє, чи є ціле число парним."""
    if not _is_integer(n):
        raise TypeError("is_even() приймає лише цілі числа.")
    return n % 2 == 0


def factorial(n):
    """Обчислює факторіал невід'ємного цілого числа."""
    if not _is_integer(n):
        raise TypeError("factorial() приймає лише цілі числа.")
    if n < 0:
        raise ValueError("Факторіал визначено лише для невід'ємних чисел.")
    result = 1
    for factor in range(2, n + 1):
        result *= factor
    return result
