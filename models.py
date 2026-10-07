def create_route(name, ratings, country, start_city, length_km, description):
    return {
        "name": name,
        "ratings": ratings,
        "location": (country, start_city),
        "length_km": length_km,
        "description": description,
    }


def average_rating(route):
    ratings = route["ratings"]
    return sum(ratings) / len(ratings) if ratings else None


def route_country(route):
    return route["location"][0]


def route_start_city(route):
    return route["location"][1]
