"""Очищення сирого датасету маршрутів ."""
import numpy as np
import pandas as pd

from tourist_routes.core.config import MAX_LENGTH_KM, MAX_RATING, MIN_LENGTH_KM, MIN_RATING

CATEGORY_COLUMNS = ["type", "country", "difficulty", "bike_type"]


def _capitalize_first(series):
    series = series.str.strip()
    return series.str[:1].str.upper() + series.str[1:]


def remove_duplicates(df):
    return df.drop_duplicates().reset_index(drop=True)


def clean_text(df):
    df = df.copy()
    df["country"] = df["country"].str.strip().str.capitalize()
    df["start_city"] = df["start_city"].str.strip().str.capitalize()
    df["name"] = _capitalize_first(df["name"])
    df["description"] = df["description"].str.strip()
    return df


def to_numeric(df):
    df = df.copy()
    for column in ["length_km", "price_eur"]:
        df[column] = pd.to_numeric(
            df[column].astype(str).str.replace(",", ".", regex=False), errors="coerce"
        )
    return df


def drop_invalid_length(df):
    valid = df["length_km"].between(MIN_LENGTH_KM, MAX_LENGTH_KM)
    return df[valid].reset_index(drop=True)


def fill_missing(df):
    """Від'ємна ціна -> пропуск; пропуски ціни -> медіана за типом; опис -> заглушка."""
    df = df.copy()
    df.loc[df["price_eur"] < 0, "price_eur"] = np.nan
    median_price = df.groupby("type")["price_eur"].transform("median")
    df["price_eur"] = df["price_eur"].fillna(median_price).round(2)
    df["description"] = df["description"].fillna("Опис відсутній")
    return df


def parse_ratings(raw):
    if pd.isna(raw):
        return np.nan
    return [int(part) for part in str(raw).split()]


def _ratings_valid(values):
    return isinstance(values, list) and all(MIN_RATING <= v <= MAX_RATING for v in values)


def validate_ratings(df):
    """Додає ratings_list; записи з оцінками поза 1–10 вважає такими, що відгуків немає."""
    df = df.copy()
    df["ratings_list"] = df["ratings"].apply(parse_ratings)
    has_ratings = df["ratings_list"].apply(lambda v: isinstance(v, list))
    invalid = has_ratings & ~df["ratings_list"].apply(_ratings_valid)
    df.loc[invalid, ["ratings", "ratings_list"]] = np.nan
    return df


def convert_types(df):
    df = df.copy()
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    for column in CATEGORY_COLUMNS:
        df[column] = df[column].astype("category")
    df["elevation_gain_m"] = df["elevation_gain_m"].astype("Int64")
    df["stops_count"] = df["stops_count"].astype("Int64")
    return df


def clean(df):
    df = remove_duplicates(df)
    df = clean_text(df)
    df = to_numeric(df)
    df = drop_invalid_length(df)
    df = fill_missing(df)
    df = validate_ratings(df)
    return convert_types(df)
