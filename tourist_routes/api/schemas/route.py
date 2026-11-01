from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tourist_routes.core.config import (
    MAX_DESCRIPTION_LENGTH,
    MAX_ELEVATION_M,
    MAX_LENGTH_KM,
    MAX_NAME_LENGTH,
    MAX_RATING,
    MAX_STOPS,
    MIN_ELEVATION_M,
    MIN_LENGTH_KM,
    MIN_RATING,
    MIN_STOPS,
)

RouteType = Literal["Route", "HikingRoute", "CyclingRoute", "BusTour"]
Rating = Annotated[Union[int, float], Field(ge=MIN_RATING, le=MAX_RATING)]

# Які додаткові поля обов'язкові для кожного типу маршруту.
REQUIRED_EXTRAS = {
    "Route": (),
    "HikingRoute": ("difficulty", "elevation_gain_m"),
    "CyclingRoute": ("bike_type",),
    "BusTour": ("stops_count",),
}
ALL_EXTRAS = ("difficulty", "elevation_gain_m", "bike_type", "stops_count")


class RouteCreate(BaseModel):
    """Тіло запиту для створення (POST) і повної заміни (PUT) маршруту."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "type": "HikingRoute",
                    "name": "Карпатська мандрівка",
                    "country": "Україна",
                    "start_city": "Ворохта",
                    "length_km": 45,
                    "description": "Триденний похід через полонини.",
                    "ratings": [9, 10, 8],
                    "difficulty": "середній",
                    "elevation_gain_m": 1800,
                }
            ]
        },
    )

    type: RouteType
    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    country: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    start_city: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    length_km: float = Field(ge=MIN_LENGTH_KM, le=MAX_LENGTH_KM)
    description: str = Field(min_length=1, max_length=MAX_DESCRIPTION_LENGTH)
    ratings: list[Rating] = Field(default_factory=list)

    difficulty: Optional[Literal["легкий", "середній", "складний"]] = None
    elevation_gain_m: Optional[float] = Field(default=None, ge=MIN_ELEVATION_M, le=MAX_ELEVATION_M)
    bike_type: Optional[Literal["шосейний", "гірський", "міський"]] = None
    stops_count: Optional[int] = Field(default=None, ge=MIN_STOPS, le=MAX_STOPS)

    @model_validator(mode="after")
    def check_type_specific_fields(self):
        required = REQUIRED_EXTRAS[self.type]
        missing = [field for field in required if getattr(self, field) is None]
        if missing:
            raise ValueError(f"Для типу {self.type} обов'язкові поля: {', '.join(missing)}.")
        for field in ALL_EXTRAS:
            if field not in required:
                setattr(self, field, None)
        return self


class RouteRead(RouteCreate):
    """Відповідь API: дані маршруту + обчислені показники з доменних класів."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    average_rating: Optional[float] = None
    estimated_duration_hours: Optional[float] = None
