"""Простий банківський рахунок із перевіркою сум."""


def _check_amount(amount, what):
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise TypeError(f"{what}: потрібне числове значення.")
    if amount != amount or amount in (float("inf"), float("-inf")):
        raise ValueError(f"{what}: потрібне скінченне число.")
    if amount <= 0:
        raise ValueError(f"{what}: сума має бути більшою за нуль.")


class BankAccount:
    def __init__(self, initial_balance=0):
        if isinstance(initial_balance, bool) or not isinstance(initial_balance, (int, float)):
            raise TypeError("Початковий баланс має бути числом.")
        if initial_balance < 0:
            raise ValueError("Початковий баланс не може бути від'ємним.")
        self._balance = initial_balance

    def deposit(self, amount):
        """Додає кошти на рахунок. Сума має бути додатною."""
        _check_amount(amount, "Поповнення")
        self._balance += amount
        return self._balance

    def withdraw(self, amount):
        """Знімає кошти. Не можна зняти більше, ніж є на рахунку."""
        _check_amount(amount, "Зняття")
        if amount > self._balance:
            raise ValueError("Недостатньо коштів на рахунку.")
        self._balance -= amount
        return self._balance

    def get_balance(self):
        return self._balance
