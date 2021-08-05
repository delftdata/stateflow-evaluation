import stateflow
from benchmark.hotel.search import Geo
from benchmark.hotel.search import Search
from benchmark.hotel.profile import Profile, HotelProfile
from benchmark.hotel.rate import Rate
from benchmark.hotel.reservation import Reservation


from typing import List


@stateflow.stateflow
class Frontend:
    # Actually we use the ../frontend.py
    def __init__(self, frontend_id: str):
        self.frontend_id = frontend_id

    # def search(self, in_date: str, out_date: str, lat: str, lon: str) -> HotelProfile:
    #     current_id = int(self.frontend_id)
    #
    #     print("I'M HERE")
    #
    #     geo: Geo = stateflow.service_by_id(Geo, f"geo_{current_id}")
    #     rate: Rate = stateflow.service_by_id(Rate, f"rate_{current_id}")
    #     profile: Profile = stateflow.service_by_id(Profile, f"profile_{current_id}")
    #     search: Search = stateflow.service_by_id(Search, f"search_{current_id}")
    #
    #     nearby_hotels: List[str] = search.nearby(lat, lon, geo, rate)
    #
    #     print(nearby_hotels)
    #
    #     available_hotels: List[str] = []
    #
    #     for hotel in nearby_hotels:
    #         reservation: Reservation = stateflow.service_by_id(Reservation, hotel)
    #         is_available: bool = reservation.check_availability(in_date, out_date, 1)
    #
    #         if is_available:
    #             available_hotels += []
    #
    #     profiles: List[HotelProfile] = profile.get_profiles(available_hotels)
    #     return profiles

    def __key__(self):
        return "frontend_" + self.frontend_id
