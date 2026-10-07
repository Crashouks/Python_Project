import services
from config import MIN_RATING
from display import print_route, print_routes, print_statistics
from input_utils import read_number, read_route_data, read_route_id
from models import create_route
from repository import all_routes, find_route, remove_route, replace_route, save_route

NOT_FOUND_MESSAGE = "Маршрут з таким ID не знайдено.\n"
EMPTY_LIST_MESSAGE = "Список маршрутів порожній."


def ask_for_route(prompt):
    route_id = read_route_id(prompt)
    if route_id is None:
        return None
    route = find_route(route_id)
    if route is None:
        print(NOT_FOUND_MESSAGE)
        return None
    return route_id, route


def handle_add():
    route = create_route(*read_route_data())
    route_id = save_route(route)
    print(f"Маршрут «{route['name']}» додано з ID: {route_id}\n")


def handle_edit():
    found = ask_for_route("Введіть ID маршруту для редагування: ")
    if found is None:
        return
    route_id, route = found
    print(f"Редагуємо маршрут «{route['name']}» (Enter — залишити поточне значення)")
    replace_route(route_id, create_route(*read_route_data(existing=route)))
    print("Дані маршруту оновлено!\n")


def handle_delete():
    found = ask_for_route("Введіть ID маршруту для видалення: ")
    if found is None:
        return
    route_id, _ = found
    deleted = remove_route(route_id)
    print(f"Маршрут «{deleted['name']}» видалено.\n")


def handle_show_all():
    print_routes(all_routes(), EMPTY_LIST_MESSAGE)


def handle_search_by_id():
    found = ask_for_route("Введіть ID маршруту: ")
    if found is not None:
        print_route(*found)


def handle_search_by_name():
    query = input("Введіть назву (або її частину) для пошуку: ")
    print_routes(services.find_by_name(query), "Маршрутів з такою назвою не знайдено.")


def handle_search_by_country():
    query = input("Введіть країну для пошуку: ")
    print_routes(services.find_by_country(query), "Маршрутів у цій країні не знайдено.")


def handle_filter_by_length():
    min_length = read_number("Мінімальна протяжність (км)", float, 0, min_value=0)
    max_length = read_number("Максимальна протяжність (км)", float, min_value=min_length)
    print_routes(
        services.filter_by_length(min_length, max_length),
        "Маршрутів у цьому діапазоні не знайдено.",
    )


def handle_filter_by_rating():
    min_average = read_number("Мінімальний середній бал", float, min_value=MIN_RATING)
    print_routes(
        services.filter_by_rating(min_average), "Маршрутів з таким рейтингом не знайдено."
    )


def handle_sort_by_rating():
    print_routes(services.sort_by_rating(), EMPTY_LIST_MESSAGE)


def handle_sort_by_length():
    print_routes(services.sort_by_length(), EMPTY_LIST_MESSAGE)


def handle_statistics():
    print_statistics(services.build_statistics())
