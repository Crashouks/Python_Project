"""Групування й агрегація ."""
import pandas as pd


def by_type(df):
    return df.groupby("type", observed=True)["length_km"].agg(
        ["count", "sum", "mean", "min", "max"]
    ).round(2)


def by_country(df):
    return (
        df.groupby("country", observed=True)
        .agg(routes=("route_id", "count"), total_km=("length_km", "sum"),
             avg_length_km=("length_km", "mean"), min_length_km=("length_km", "min"),
             max_length_km=("length_km", "max"), avg_rating=("avg_rating", "mean"),
             avg_price_eur=("price_eur", "mean"))
        .round(2)
        .sort_values("routes", ascending=False)
    )


def by_country_and_type(df):
    return (
        df.groupby(["country", "type"], observed=True)
        .agg(routes=("route_id", "count"), avg_length_km=("length_km", "mean"),
             avg_rating=("avg_rating", "mean"), avg_price_eur=("price_eur", "mean"))
        .round(2)
        .reset_index()
    )


def count_pivot(df):
    return pd.pivot_table(df, index="country", columns="type", values="route_id",
                          aggfunc="count", fill_value=0, observed=True)
