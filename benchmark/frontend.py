from benchmark.hotel.user import User
from benchmark.hotel.search import Search, Geo, Rate
from benchmark.hotel.reservation import Reservation
from benchmark.hotel.profile import Profile, HotelProfile
from benchmark.hotel.recommend import RecommendType, Recommend
from typing import List

import stateflow
import asyncio
from stateflow import service_by_id
from stateflow.client.fastapi.kafka import KafkaFastAPIClient, StateflowFailure


client = KafkaFastAPIClient(stateflow.init())
app = client.get_app()


@app.get("/search")
async def search(lat: float, lon: float, in_date: str, out_date: str):
    # Here we select the 'partitioned services'.
    search: Search = Search.by_id("search-service-1")
    geo: Geo = Geo.by_id("geo-service-1")
    rate: Rate = Rate.by_id("rate-service-1")
    profile: Profile = Profile.by_id("profile-service-1")

    # Find nearby hotels.
    nearby_hotels: List[str] = await search.nearby(lat, lon, geo, rate)

    # All available hotels.
    available_hotels: List[str] = []

    # TODO, make this run parallel.
    for hotel_id in nearby_hotels:
        reservation: Reservation = Reservation.by_id(hotel_id)
        is_available: bool = await reservation.check_availability(in_date, out_date, 1)

        if is_available:
            available_hotels.append(hotel_id)

    profiles: List[HotelProfile] = await profile.get_profiles(available_hotels)
    return profiles


@app.get("/recommend")
async def recommend(
    recommendation_type: RecommendType, lat: float = 0.0, lon: float = 0.0
):
    # Here we select the 'partitioned services'.
    recommend: Recommend = Recommend.by_id("recommend-service-1")
    profile: Profile = Profile.by_id("profile-service-1")

    # Get recommendations.
    recommendations: List[str] = await recommend.recommend(
        recommendation_type, {"lat": lat, "lon": lon}
    )

    # Get all profiles of recommended hotels.
    profiles: List[HotelProfile] = await profile.get_profiles(recommendations)

    return profiles


@app.get("/reserve")
async def reserve(
    in_date: str,
    out_date: str,
    hotel_id: str,
    customer_name: str,
    amount_of_rooms: int,
    username: str,
    password: str,
):
    user: User = User.by_id(username)

    # Login the user first.
    login_success: bool = await user.login(password)

    # Get hotel reservation system (i.e. stateful function).
    reserve: Reservation = Reservation.by_id(hotel_id)

    # Try to make the reservation.
    reserve_success: bool = await reserve.add_reservation(customer_name, in_date, out_date, amount_of_rooms)

    return reserve_success


@app.get("/login")
async def user(username: str, password: str):
    user: User = User.by_id(username)

    # Login the user.
    login_success: bool = await user.login(password)

    return login_success
