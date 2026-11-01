"""Створення нових стовпців (ЛР 3, розділ 5 завдання)."""
import numpy as np
import pandas as pd

from tourist_routes.core.config import MAX_LENGTH_KM

SPEED_KMH = {"Route": 5.0, "HikingRoute": 4.0, "CyclingRoute": 15.0, "BusTour": 40.0}
MOUNTAIN_BIKE_SPEED_KMH = 10.0
METERS_PER_EXTRA_HOUR = 600
HOURS_PER_STOP = 0.25
LENGTH_BINS = [0, 20, 100, 300, MAX_LENGTH_KM]
LENGTH_LABELS = ["коротка", "середня", "довга", "дуже довга"]
SEED = 42


def estimated_duration_hours(df):
    """Та сама логіка, що й estimated_duration_hours() у класах ЛР 2."""
    speed = df["type"].astype(str).map(SPEED_KMH)
    mountain = (df["type"] == "CyclingRoute") & (df["bike_type"] == "гірський")
    speed = speed.where(~mountain, MOUNTAIN_BIKE_SPEED_KMH)
    hours = df["length_km"] / speed
    hours += df["elevation_gain_m"].fillna(0).astype(float) / METERS_PER_EXTRA_HOUR
    hours += df["stops_count"].fillna(0).astype(float) * HOURS_PER_STOP
    return hours.round(2)


def add_features(df, seed=SEED):
    df = df.copy()
    df["avg_rating"] = (
        df["ratings_list"].apply(lambda v: np.mean(v) if isinstance(v, list) else np.nan).round(2)
    )
    df["ratings_count"] = df["ratings_list"].apply(lambda v: len(v) if isinstance(v, list) else 0)
    df["duration_hours"] = estimated_duration_hours(df)
    df["price_per_km"] = (df["price_eur"] / df["length_km"]).round(2)
    df["length_class"] = pd.cut(df["length_km"], bins=LENGTH_BINS, labels=LENGTH_LABELS)
    df["year_added"] = df["date_added"].dt.year.astype("Int64")
    df["popularity_score"] = np.random.default_rng(seed).integers(50, 101, size=len(df))
    return df
