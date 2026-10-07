from config import HIGH_RATING
from models import average_rating, route_country
from repository import all_routes, select_routes


def find_by_name(query):
    query = query.strip().lower()
    return select_routes(lambda route: query in route["name"].lower())


def find_by_country(query):
    query = query.strip().lower()
    return select_routes(lambda route: query in route_country(route).lower())


def filter_by_length(min_length, max_length):
    return select_routes(lambda route: min_length <= route["length_km"] <= max_length)


def filter_by_rating(min_average):
    def has_min_average(route):
        average = average_rating(route)
        return average is not None and average >= min_average

    return select_routes(has_min_average)


def sort_routes(key_func, reverse=False):
    return sorted(all_routes(), key=lambda pair: key_func(pair[1]), reverse=reverse)


def sort_by_rating():
    return sort_routes(lambda route: average_rating(route) or 0, reverse=True)


def sort_by_length():
    return sort_routes(lambda route: route["length_km"])


def collect_ratings(pairs):
    return [rating for _, route in pairs for rating in route["ratings"]]


def count_by_country(pairs):
    counts = {}
    for _, route in pairs:
        country = route_country(route)
        counts[country] = counts.get(country, 0) + 1
    return counts


def build_rating_statistics(pairs):
    ratings = collect_ratings(pairs)
    if not ratings:
        return None
    rated_pairs = [pair for pair in pairs if pair[1]["ratings"]]
    return {
        "average": sum(ratings) / len(ratings),
        "max": max(ratings),
        "min": min(ratings),
        "high_count": len([rating for rating in ratings if rating >= HIGH_RATING]),
        "best": max(rated_pairs, key=lambda pair: average_rating(pair[1])),
    }


def build_statistics():
    pairs = all_routes()
    if not pairs:
        return None
    lengths = [route["length_km"] for _, route in pairs]
    return {
        "total": len(pairs),
        "average_length": sum(lengths) / len(lengths),
        "longest": max(pairs, key=lambda pair: pair[1]["length_km"]),
        "shortest": min(pairs, key=lambda pair: pair[1]["length_km"]),
        "ratings": build_rating_statistics(pairs),
        "by_country": count_by_country(pairs),
    }
