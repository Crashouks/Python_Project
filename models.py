from dataclasses import dataclass
from typing import Optional

from config import (
    BIKE_TYPES,
    DIFFICULTY_LEVELS,
    MAX_DESCRIPTION_LENGTH,
    MAX_ELEVATION_M,
    MAX_LENGTH_KM,
    MAX_NAME_LENGTH,
    MAX_STOPS,
    MIN_ELEVATION_M,
    MIN_LENGTH_KM,
    MIN_STOPS,
)
from validators import (
    parse_number,
    validate_choice,
    validate_integer,
    validate_location,
    validate_number,
    validate_rating,
    validate_ratings,
    validate_text,
)

CHOICE = "choice"
INTEGER = "int"
DECIMAL = "float"


@dataclass(frozen=True)
class ExtraField:
    attribute: str
    label: str
    kind: str
    choices: tuple = ()
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    @property
    def prompt(self):
        if self.choices:
            return f"{self.label} ({'/'.join(self.choices)})"
        return self.label

    def parse(self, raw):
        if self.kind == INTEGER:
            return parse_number(raw, self.label, int)
        if self.kind == DECIMAL:
            return parse_number(raw, self.label, float)
        return raw

    def validate(self, value):
        if self.kind == CHOICE:
            return validate_choice(value, self.label, self.choices)
        if self.kind == INTEGER:
            return validate_integer(value, self.label, self.min_value, self.max_value)
        return validate_number(value, self.label, self.min_value, self.max_value)


DIFFICULTY_FIELD = ExtraField("difficulty", "Складність", CHOICE, choices=DIFFICULTY_LEVELS)
ELEVATION_FIELD = ExtraField(
    "elevation_gain_m", "Набір висоти (м)", DECIMAL,
    min_value=MIN_ELEVATION_M, max_value=MAX_ELEVATION_M,
)
BIKE_TYPE_FIELD = ExtraField("bike_type", "Тип велосипеда", CHOICE, choices=BIKE_TYPES)
STOPS_FIELD = ExtraField(
    "stops_count", "Кількість зупинок", INTEGER,
    min_value=MIN_STOPS, max_value=MAX_STOPS,
)


class Route:
    type_name = "Загальний маршрут"
    average_speed_kmh = 5.0
    extra_fields = ()

    def __init__(self, name, ratings, country, start_city, length_km, description):
        self.name = name
        self.ratings = ratings
        self.location = (country, start_city)
        self.length_km = length_km
        self.description = description

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = validate_text(value, "Назва маршруту", MAX_NAME_LENGTH)

    @property
    def ratings(self):
        return list(self._ratings)

    @ratings.setter
    def ratings(self, value):
        self._ratings = validate_ratings(value)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = validate_location(value)

    @property
    def country(self):
        return self._location[0]

    @property
    def start_city(self):
        return self._location[1]

    @property
    def length_km(self):
        return self._length_km

    @length_km.setter
    def length_km(self, value):
        self._length_km = validate_number(value, "Протяжність (км)", MIN_LENGTH_KM, MAX_LENGTH_KM)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = validate_text(value, "Опис маршруту", MAX_DESCRIPTION_LENGTH)

    def add_rating(self, rating):
        self._ratings.append(validate_rating(rating))

    def average_rating(self):
        return sum(self._ratings) / len(self._ratings) if self._ratings else None

    def estimated_duration_hours(self):
        return self._length_km / self.average_speed_kmh

    def extra_details(self):
        return [(field.label, getattr(self, field.attribute)) for field in self.extra_fields]

    def to_dict(self):
        data = {
            "type": self.__class__.__name__,
            "name": self._name,
            "ratings": list(self._ratings),
            "location": list(self._location),
            "length_km": self._length_km,
            "description": self._description,
        }
        for field in self.extra_fields:
            data[field.attribute] = getattr(self, field.attribute)
        return data

    @classmethod
    def from_dict(cls, data):
        country, start_city = validate_location(data["location"])
        arguments = {
            "name": data["name"],
            "ratings": data["ratings"],
            "country": country,
            "start_city": start_city,
            "length_km": data["length_km"],
            "description": data["description"],
        }
        for field in cls.extra_fields:
            arguments[field.attribute] = data[field.attribute]
        return cls(**arguments)

    def __str__(self):
        return (
            f"{self.type_name}: «{self._name}» "
            f"({self.country}, {self.start_city}), {self._length_km:g} км"
        )


class HikingRoute(Route):
    type_name = "Пішохідний маршрут"
    average_speed_kmh = 4.0
    extra_fields = (DIFFICULTY_FIELD, ELEVATION_FIELD)
    meters_per_extra_hour = 600

    def __init__(self, name, ratings, country, start_city, length_km, description,
                 difficulty, elevation_gain_m):
        super().__init__(name, ratings, country, start_city, length_km, description)
        self.difficulty = difficulty
        self.elevation_gain_m = elevation_gain_m

    @property
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, value):
        self._difficulty = DIFFICULTY_FIELD.validate(value)

    @property
    def elevation_gain_m(self):
        return self._elevation_gain_m

    @elevation_gain_m.setter
    def elevation_gain_m(self, value):
        self._elevation_gain_m = ELEVATION_FIELD.validate(value)

    def estimated_duration_hours(self):
        return super().estimated_duration_hours() + self._elevation_gain_m / self.meters_per_extra_hour


class CyclingRoute(Route):
    type_name = "Велосипедний маршрут"
    average_speed_kmh = 15.0
    mountain_speed_kmh = 10.0
    extra_fields = (BIKE_TYPE_FIELD,)

    def __init__(self, name, ratings, country, start_city, length_km, description, bike_type):
        super().__init__(name, ratings, country, start_city, length_km, description)
        self.bike_type = bike_type

    @property
    def bike_type(self):
        return self._bike_type

    @bike_type.setter
    def bike_type(self, value):
        self._bike_type = BIKE_TYPE_FIELD.validate(value)

    def estimated_duration_hours(self):
        speed = self.mountain_speed_kmh if self._bike_type == "гірський" else self.average_speed_kmh
        return self.length_km / speed


class BusTour(Route):
    type_name = "Автобусний тур"
    average_speed_kmh = 40.0
    hours_per_stop = 0.25
    extra_fields = (STOPS_FIELD,)

    def __init__(self, name, ratings, country, start_city, length_km, description, stops_count):
        super().__init__(name, ratings, country, start_city, length_km, description)
        self.stops_count = stops_count

    @property
    def stops_count(self):
        return self._stops_count

    @stops_count.setter
    def stops_count(self, value):
        self._stops_count = STOPS_FIELD.validate(value)

    def estimated_duration_hours(self):
        return super().estimated_duration_hours() + self._stops_count * self.hours_per_stop