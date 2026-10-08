from config import HIGH_RATING


class RoutePrinter:
    SEPARATOR = "-" * 40

    @staticmethod
    def format_rating(value):
        return f"{value:.2f}" if value is not None else "немає відгуків"

    @staticmethod
    def format_duration(hours):
        total_minutes = round(hours * 60)
        whole_hours, minutes = divmod(total_minutes, 60)
        return f"{whole_hours} год {minutes} хв"

    @staticmethod
    def format_value(value):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return f"{value:g}"
        return value

    def print_route(self, route_id, route):
        print(f"ID: {route_id}")
        print(f"Тип: {route.type_name}")
        print(f"Назва: {route.name}")
        print(f"Країна / місто старту: {route.country} / {route.start_city}")
        print(f"Протяжність: {route.length_km:g} км")
        for label, value in route.extra_details():
            print(f"{label}: {self.format_value(value)}")
        print(f"Орієнтовна тривалість: {self.format_duration(route.estimated_duration_hours())}")
        print(f"Відгуки (бали): {route.ratings}")
        print(f"Середній бал: {self.format_rating(route.average_rating())}")
        print(f"Опис: {route.description}")
        print(self.SEPARATOR)

    def print_routes(self, pairs, empty_message="Нічого не знайдено."):
        if not pairs:
            print(f"{empty_message}\n")
            return
        for route_id, route in pairs:
            self.print_route(route_id, route)
        print()

    @staticmethod
    def print_route_summary(label, pair):
        route_id, route = pair
        print(f"{label}: «{route.name}» (ID {route_id}, {route.length_km:g} км)")

    def print_rating_statistics(self, stats):
        if stats is None:
            print("Відгуків ще немає.")
            return
        best_id, best_route = stats["best"]
        print(f"Середній бал по всіх відгуках: {stats['average']:.2f}")
        print(f"Максимальний бал: {stats['max']}")
        print(f"Мінімальний бал: {stats['min']}")
        print(f"Кількість балів >= {HIGH_RATING}: {stats['high_count']}")
        print(
            f"Найкращий маршрут: «{best_route.name}» (ID {best_id}, "
            f"середній бал {best_route.average_rating():.2f})"
        )

    @staticmethod
    def print_counts(title, counts):
        print(f"{title}:")
        for key, count in counts.items():
            print(f"  {key}: {count}")

    def print_statistics(self, stats):
        if stats is None:
            print("Список маршрутів порожній.\n")
            return
        print(f"Кількість маршрутів: {stats['total']}")
        print(f"Середня протяжність: {stats['average_length']:.1f} км")
        self.print_route_summary("Найдовший маршрут", stats["longest"])
        self.print_route_summary("Найкоротший маршрут", stats["shortest"])
        self.print_rating_statistics(stats["ratings"])
        self.print_counts("Маршрутів за країнами", stats["by_country"])
        self.print_counts("Маршрутів за типами", stats["by_type"])
        print()