from config import MAX_RATING, MIN_RATING
from exceptions import ValidationError
from factory import list_route_classes
from validators import parse_number, parse_ratings, validate_number, validate_text


class InputReader:
    YES_ANSWERS = ("т", "так", "y", "yes")
    NO_ANSWERS = ("н", "ні", "n", "no")

    @staticmethod
    def format_default(value):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return f"{value:g}"
        return str(value)

    def ask(self, label, converter, default=None):
        suffix = f" [{self.format_default(default)}]" if default is not None else ""
        while True:
            raw = input(f"{label}{suffix}: ").strip()
            if not raw and default is not None:
                return default
            try:
                return converter(raw)
            except ValidationError as error:
                print(error)

    def read_text(self, label, default=None, max_length=None):
        return self.ask(label, lambda raw: validate_text(raw, label, max_length), default)

    def read_number(self, label, number_type=float, default=None, min_value=None, max_value=None):
        def convert(raw):
            return validate_number(parse_number(raw, label, number_type), label, min_value, max_value)

        return self.ask(label, convert, default)

    def read_ratings(self, default=None):
        label = f"Відгуки (бали {MIN_RATING}-{MAX_RATING} через пробіл)"
        hint = ""
        if default:
            shown = " ".join(f"{rating:g}" for rating in default)
            hint = f" [{shown}] ('-' щоб очистити)"
        while True:
            raw = input(f"{label}{hint}: ").strip()
            if not raw:
                return list(default) if default else []
            if raw == "-":
                return []
            try:
                return parse_ratings(raw)
            except ValidationError as error:
                print(error)

    def read_extra_field(self, field, default=None):
        return self.ask(field.prompt, lambda raw: field.validate(field.parse(raw)), default)

    def read_route_id(self, purpose):
        while True:
            raw = input(f"Введіть ID маршруту {purpose} (Enter — скасувати): ").strip()
            if not raw:
                return None
            try:
                return validate_number(parse_number(raw, "ID", int), "ID", 1)
            except ValidationError as error:
                print(error)

    def read_route_class(self):
        route_classes = list_route_classes()
        print("Оберіть тип маршруту:")
        for number, route_class in enumerate(route_classes, start=1):
            print(f"{number}. {route_class.type_name}")

        def convert(raw):
            number = validate_number(
                parse_number(raw, "Номер типу", int), "Номер типу", 1, len(route_classes)
            )
            return route_classes[number - 1]

        return self.ask("Номер типу", convert)

    def confirm(self, question):
        while True:
            answer = input(f"{question} (т/н): ").strip().lower()
            if answer in self.YES_ANSWERS:
                return True
            if answer in self.NO_ANSWERS:
                return False
            print("Введіть «т» або «н».")
