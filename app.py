from config import DATA_FILE, MAX_RATING, MIN_RATING
from display import RoutePrinter
from exceptions import StorageError
from input_reader import InputReader
from manager import RouteManager
from menu import Menu, MenuItem
from route_form import RouteForm
from storage import JsonStorage

EMPTY_LIST_MESSAGE = "Список маршрутів порожній."


class RouteApp:
    def __init__(self, storage=None):
        self._manager = RouteManager()
        self._storage = storage or JsonStorage(DATA_FILE)
        self._reader = InputReader()
        self._form = RouteForm(self._reader)
        self._printer = RoutePrinter()
        self._has_unsaved_changes = False
        self._file_unreadable = False
        self._menu = Menu("Туристичні маршрути", self._build_menu_items(), can_exit=self._can_exit)

    def _build_menu_items(self):
        return [
            MenuItem("Додати маршрут", self.add_route),
            MenuItem("Показати всі маршрути", self.show_all_routes),
            MenuItem("Пошук за ID", self.search_by_id),
            MenuItem("Пошук за назвою", self.search_by_name),
            MenuItem("Пошук за країною", self.search_by_country),
            MenuItem("Фільтр за типом маршруту", self.filter_by_type),
            MenuItem("Фільтр за протяжністю", self.filter_by_length),
            MenuItem("Фільтр за середнім балом", self.filter_by_rating),
            MenuItem("Сортувати за рейтингом", self.sort_by_rating),
            MenuItem("Сортувати за протяжністю", self.sort_by_length),
            MenuItem("Сортувати за тривалістю", self.sort_by_duration),
            MenuItem("Редагувати маршрут", self.edit_route),
            MenuItem("Видалити маршрут", self.delete_route),
            MenuItem("Статистика", self.show_statistics),
            MenuItem("Зберегти у JSON-файл", self.save_to_file),
            MenuItem("Завантажити з JSON-файлу", self.load_from_file),
        ]

    def run(self):
        self._load_on_start()
        self._menu.run()

    def _load_on_start(self):
        try:
            self._manager.replace_all(self._storage.load())
        except StorageError as error:
            self._file_unreadable = True
            print(f"Помилка: {error}\n")
        else:
            print(f"Завантажено маршрутів: {len(self._manager)} (файл {self._storage.filename})\n")

    def _can_exit(self):
        if not self._has_unsaved_changes:
            return True
        if not self._reader.confirm("Є незбережені зміни. Зберегти у файл?"):
            return True
        try:
            self.save_to_file()
        except StorageError as error:
            print(f"Помилка: {error}\n")
            return False
        return not self._has_unsaved_changes

    def add_route(self):
        route_class = self._reader.read_route_class()
        route = self._form.build(route_class)
        route_id = self._manager.add(route)
        self._has_unsaved_changes = True
        print(f"Маршрут «{route.name}» додано з ID: {route_id}\n")

    def edit_route(self):
        route_id = self._reader.read_route_id("для редагування")
        if route_id is None:
            return
        route = self._manager.get(route_id)
        print(f"Редагуємо: {route} (Enter — залишити поточне значення)")
        self._manager.replace(route_id, self._form.build(route.__class__, existing=route))
        self._has_unsaved_changes = True
        print("Дані маршруту оновлено!\n")

    def delete_route(self):
        route_id = self._reader.read_route_id("для видалення")
        if route_id is None:
            return
        route = self._manager.get(route_id)
        if not self._reader.confirm(f"Видалити маршрут «{route.name}»?"):
            print("Видалення скасовано.\n")
            return
        self._manager.remove(route_id)
        self._has_unsaved_changes = True
        print(f"Маршрут «{route.name}» видалено.\n")

    def show_all_routes(self):
        self._printer.print_routes(self._manager.all(), EMPTY_LIST_MESSAGE)

    def search_by_id(self):
        route_id = self._reader.read_route_id("для пошуку")
        if route_id is not None:
            self._printer.print_route(route_id, self._manager.get(route_id))

    def search_by_name(self):
        query = input("Введіть назву (або її частину) для пошуку: ")
        self._printer.print_routes(
            self._manager.find_by_name(query), "Маршрутів з такою назвою не знайдено."
        )

    def search_by_country(self):
        query = input("Введіть країну для пошуку: ")
        self._printer.print_routes(
            self._manager.find_by_country(query), "Маршрутів у цій країні не знайдено."
        )

    def filter_by_type(self):
        route_class = self._reader.read_route_class()
        self._printer.print_routes(
            self._manager.filter_by_type(route_class), "Маршрутів цього типу не знайдено."
        )

    def filter_by_length(self):
        min_length = self._reader.read_number("Мінімальна протяжність (км)", float, 0, 0)
        max_length = self._reader.read_number(
            "Максимальна протяжність (км)", float, min_value=min_length
        )
        self._printer.print_routes(
            self._manager.filter_by_length(min_length, max_length),
            "Маршрутів у цьому діапазоні не знайдено.",
        )

    def filter_by_rating(self):
        min_average = self._reader.read_number(
            "Мінімальний середній бал", float, min_value=MIN_RATING, max_value=MAX_RATING
        )
        self._printer.print_routes(
            self._manager.filter_by_rating(min_average), "Маршрутів з таким рейтингом не знайдено."
        )

    def sort_by_rating(self):
        self._printer.print_routes(self._manager.sort_by_rating(), EMPTY_LIST_MESSAGE)

    def sort_by_length(self):
        self._printer.print_routes(self._manager.sort_by_length(), EMPTY_LIST_MESSAGE)

    def sort_by_duration(self):
        self._printer.print_routes(self._manager.sort_by_duration(), EMPTY_LIST_MESSAGE)

    def show_statistics(self):
        self._printer.print_statistics(self._manager.statistics())

    def save_to_file(self):
        if self._file_unreadable and not self._reader.confirm(
            f"Файл {self._storage.filename} не вдалося прочитати. Перезаписати його?"
        ):
            print("Збереження скасовано.\n")
            return
        self._storage.save(self._manager.routes())
        self._file_unreadable = False
        self._has_unsaved_changes = False
        print(f"Збережено маршрутів: {len(self._manager)} (файл {self._storage.filename})\n")

    def load_from_file(self):
        if self._has_unsaved_changes and not self._reader.confirm(
            "Незбережені зміни буде втрачено. Продовжити?"
        ):
            print("Завантаження скасовано.\n")
            return
        self._manager.replace_all(self._storage.load())
        self._file_unreadable = False
        self._has_unsaved_changes = False
        print(f"Завантажено маршрутів: {len(self._manager)} (файл {self._storage.filename})\n")
