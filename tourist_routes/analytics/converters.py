"""Зв'язок ЛР 2 і ЛР 3: об'єкти Route -> pandas DataFrame."""
import pandas as pd

from tourist_routes.analytics.features import add_features
from tourist_routes.core.config import MAX_RATING, MIN_RATING


def routes_to_dataframe(routes):
    """Перетворює список Route (з ЛР 2) на DataFrame тієї ж структури, що й датасет ЛР 3."""
    rows = []
    for route_id, route in enumerate(routes, start=1):
        data = route.to_dict()
        rows.append({
            "route_id": route_id,
            "type": data["type"],
            "name": data["name"],
            "country": route.country,
            "start_city": route.start_city,
            "length_km": data["length_km"],
            "description": data["description"],
            "ratings": " ".join(map(str, data["ratings"])) or None,
            "ratings_list": list(data["ratings"]) or float("nan"),
            "difficulty": data.get("difficulty"),
            "elevation_gain_m": data.get("elevation_gain_m"),
            "bike_type": data.get("bike_type"),
            "stops_count": data.get("stops_count"),
            "price_eur": None,
            "date_added": pd.NaT,
        })
    df = pd.DataFrame(rows)
    df["elevation_gain_m"] = df["elevation_gain_m"].astype("Int64")
    df["stops_count"] = df["stops_count"].astype("Int64")
    df["date_added"] = pd.to_datetime(df["date_added"])
    df["price_eur"] = pd.to_numeric(df["price_eur"])
    return add_features(df)


__all__ = ["routes_to_dataframe", "MIN_RATING", "MAX_RATING"]
