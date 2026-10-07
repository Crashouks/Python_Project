from config import HIGH_RATING
from models import average_rating, route_start_city, route_country

SEPARATOR = "-" * 40


def format_rating(value):
    return f"{value:.2f}" if value is not None else "немає відгуків"


def print_route(route_id, route):
    print(f"ID: {route_id}")
    print(f"Назва: {route['name']}")
    print(f"Країна / місто старту: {route_country(route)} / {route_start_city(route)}")
    print(f"Протяжність: {route['length_km']:g} км")
    print(f"Відгуки (бали): {route['ratings']}")
    print(f"Середній бал: {format_rating(average_rating(route))}")
    print(f"Опис: {route['description']}")
    print(SEPARATOR)


def print_routes(pairs, empty_message="Нічого не знайдено."):
    if not pairs:
        print(f"{empty_message}\n")
        return
    for route_id, route in pairs:
        print_route(route_id, route)
    print()


def print_route_summary(label, pair):
    route_id, route = pair
    print(f"{label}: «{route['name']}» (ID {route_id}, {route['length_km']:g} км)")


def print_rating_statistics(stats):
    if stats is None:
        print("Відгуків ще немає.")
        return
    best_id, best_route = stats["best"]
    print(f"Середній бал по всіх відгуках: {stats['average']:.2f}")
    print(f"Максимальний бал: {stats['max']}")
    print(f"Мінімальний бал: {stats['min']}")
    print(f"Кількість балів >= {HIGH_RATING}: {stats['high_count']}")
    print(
        f"Найкращий маршрут: «{best_route['name']}» (ID {best_id}, "
        f"середній бал {average_rating(best_route):.2f})"
    )


def print_country_statistics(by_country):
    print("Маршрутів за країнами:")
    for country, count in by_country.items():
        print(f"  {country}: {count}")


def print_statistics(stats):
    if stats is None:
        print("Список маршрутів порожній.\n")
        return
    print(f"Кількість маршрутів: {stats['total']}")
    print(f"Середня протяжність: {stats['average_length']:.1f} км")
    print_route_summary("Найдовший маршрут", stats["longest"])
    print_route_summary("Найкоротший маршрут", stats["shortest"])
    print_rating_statistics(stats["ratings"])
    print_country_statistics(stats["by_country"])
    print()
