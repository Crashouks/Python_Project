from config import HIGH_RATING


class RouteStatistics:
    def __init__(self, pairs):
        self._pairs = list(pairs)

    def total(self):
        return len(self._pairs)

    def average_length(self):
        return sum(route.length_km for _, route in self._pairs) / len(self._pairs)

    def longest(self):
        return max(self._pairs, key=lambda pair: pair[1].length_km)

    def shortest(self):
        return min(self._pairs, key=lambda pair: pair[1].length_km)

    def all_ratings(self):
        return [rating for _, route in self._pairs for rating in route.ratings]

    def rating_summary(self):
        ratings = self.all_ratings()
        if not ratings:
            return None
        rated_pairs = [pair for pair in self._pairs if pair[1].ratings]
        return {
            "average": sum(ratings) / len(ratings),
            "max": max(ratings),
            "min": min(ratings),
            "high_count": len([rating for rating in ratings if rating >= HIGH_RATING]),
            "best": max(rated_pairs, key=lambda pair: pair[1].average_rating()),
        }

    def count_by(self, key_func):
        counts = {}
        for _, route in self._pairs:
            key = key_func(route)
            counts[key] = counts.get(key, 0) + 1
        return counts

    def summary(self):
        if not self._pairs:
            return None
        return {
            "total": self.total(),
            "average_length": self.average_length(),
            "longest": self.longest(),
            "shortest": self.shortest(),
            "ratings": self.rating_summary(),
            "by_country": self.count_by(lambda route: route.country),
            "by_type": self.count_by(lambda route: route.type_name),
        }
