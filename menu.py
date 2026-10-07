import actions

EXIT_CHOICE = "0"

MENU_ITEMS = {
    "1": ("Додати маршрут", actions.handle_add),
    "2": ("Показати всі маршрути", actions.handle_show_all),
    "3": ("Пошук за ID", actions.handle_search_by_id),
    "4": ("Пошук за назвою", actions.handle_search_by_name),
    "5": ("Пошук за країною", actions.handle_search_by_country),
    "6": ("Фільтр за протяжністю", actions.handle_filter_by_length),
    "7": ("Фільтр за середнім балом", actions.handle_filter_by_rating),
    "8": ("Сортувати за рейтингом", actions.handle_sort_by_rating),
    "9": ("Сортувати за протяжністю", actions.handle_sort_by_length),
    "10": ("Редагувати маршрут", actions.handle_edit),
    "11": ("Видалити маршрут", actions.handle_delete),
    "12": ("Статистика", actions.handle_statistics),
}


def print_menu():
    print("==== Туристичні маршрути ====")
    for key, (title, _) in MENU_ITEMS.items():
        print(f"{key}. {title}")
    print(f"{EXIT_CHOICE}. Вихід")


def run_menu():
    while True:
        print_menu()
        choice = input("Ваш вибір: ").strip()

        if choice in MENU_ITEMS:
            MENU_ITEMS[choice][1]()
        elif choice == EXIT_CHOICE:
            print("Вихід з програми...")
            break
        else:
            print("Невірний вибір, спробуйте ще раз.\n")
