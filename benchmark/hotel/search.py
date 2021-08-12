import stateflow
from benchmark.hotel.geo import Geo
from typing import List
from benchmark.hotel.rate import Rate, RatePlan


@stateflow.stateflow
class Search:
    def __init__(self, search_id: str):
        self.search_id = search_id

    def nearby(self, lat: str, lon: str, geo: Geo, rate: Rate) -> List[str]:
        nearby_hotels: List[str] = geo.nearby(lat, lon)
        rate_plans: List[RatePlan] = rate.get_rates(nearby_hotels)

        hotel_ids: List[str] = []
        for plan in rate_plans:
            hotel_ids = hotel_ids + [
                plan.hotelId
            ]  # We use immutable types, because its a requirement of Stateflow.

        return hotel_ids

    def __key__(self):
        return self.search_id
