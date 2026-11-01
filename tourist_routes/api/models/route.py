from typing import Optional

from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from tourist_routes.api.database import Base
from tourist_routes.core.factory import route_from_dict

EXTRA_COLUMNS = ("difficulty", "elevation_gain_m", "bike_type", "stops_count")


class RouteRecord(Base):
    """Таблиця маршрутів: один рядок = один Route/HikingRoute/CyclingRoute/BusTour."""

    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))
    start_city: Mapped[str] = mapped_column(String(100))
    length_km: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(String(1000))
    ratings: Mapped[list] = mapped_column(JSON, default=list)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    elevation_gain_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bike_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    stops_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def to_domain(self):
        """Перетворює запис БД на об'єкт доменної моделі (core.models)."""
        data = {
            "type": self.type,
            "name": self.name,
            "ratings": list(self.ratings or []),
            "location": [self.country, self.start_city],
            "length_km": self.length_km,
            "description": self.description,
        }
        for column in EXTRA_COLUMNS:
            data[column] = getattr(self, column)
        return route_from_dict(data)

    @classmethod
    def from_domain(cls, route):
        data = route.to_dict()
        country, start_city = data.pop("location")
        return cls(country=country, start_city=start_city, **data)
