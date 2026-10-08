from config import DEMO_FILE
from display import RoutePrinter
from exceptions import ValidationError
from manager import RouteManager
from models import CyclingRoute, HikingRoute, Route
from sample_data import create_sample_routes
from storage import JsonStorage


def demo_creation(manager, printer):
    for route in create_sample_routes():
        manager.add(route)
    print("=== Створені маршрути ===")
    printer.print_routes(manager.all())


def demo_saving(manager, storage):
    storage.save(manager.routes())
    print(f"=== Дані збережено у файл {storage.filename} ===\n")


def demo_loading(storage, printer):
    loaded_manager = RouteManager()
    loaded_manager.replace_all(storage.load())
    print("=== Маршрути, зчитані з файлу ===")
    printer.print_routes(loaded_manager.all())
    return loaded_manager


def demo_polymorphism(manager, printer):
    print("=== Поліморфізм: орієнтовна тривалість для різних типів ===")
    for _, route in manager.all():
        duration = printer.format_duration(route.estimated_duration_hours())
        print(f"{route} -> {duration}")
    print()


def demo_validation():
    print("=== Захист від некоректних даних ===")
    invalid_attempts = [
        lambda: Route("", [9], "Україна", "Київ", 10, "Опис"),
        lambda: Route("Тест", [15], "Україна", "Київ", 10, "Опис"),
        lambda: Route("Тест", [9], "Україна", "Київ", -5, "Опис"),
        lambda: HikingRoute("Тест", [9], "Україна", "Київ", 10, "Опис", "неможливий", 100),
        lambda: CyclingRoute("Тест", [9], "Україна", "Київ", "багато", "Опис", "гірський"),
    ]
    for attempt in invalid_attempts:
        try:
            attempt()
        except ValidationError as error:
            print(f"Відхилено: {error}")
    print()


def main():
    printer = RoutePrinter()
    storage = JsonStorage(DEMO_FILE)
    manager = RouteManager()

    demo_creation(manager, printer)
    demo_saving(manager, storage)
    loaded_manager = demo_loading(storage, printer)
    demo_polymorphism(loaded_manager, printer)
    demo_validation()


if __name__ == "__main__":
    main()
