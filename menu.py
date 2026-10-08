from dataclasses import dataclass
from typing import Callable

from exceptions import RouteError


@dataclass(frozen=True)
class MenuItem:
    title: str
    handler: Callable


class Menu:
    EXIT_CHOICE = "0"

    def __init__(self, title, items, can_exit=None):
        self._title = title
        self._items = {str(number): item for number, item in enumerate(items, start=1)}
        self._can_exit = can_exit

    def _print(self):
        print(f"==== {self._title} ====")
        for number, item in self._items.items():
            print(f"{number}. {item.title}")
        print(f"{self.EXIT_CHOICE}. Вихід")

    @staticmethod
    def _run_item(item):
        try:
            item.handler()
        except RouteError as error:
            print(f"Помилка: {error}\n")

    def run(self):
        while True:
            self._print()
            choice = input("Ваш вибір: ").strip()

            if choice in self._items:
                self._run_item(self._items[choice])
            elif choice == self.EXIT_CHOICE:
                if self._can_exit is None or self._can_exit():
                    print("Вихід з програми...")
                    break
            else:
                print("Невірний вибір, спробуйте ще раз.\n")