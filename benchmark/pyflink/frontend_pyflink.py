import os
import sys

IS_PYFLINK = bool(os.getenv("PYFLINK"))


if IS_PYFLINK:
    from user import User
    from search import Search, Geo, Rate
    from reservation import Reservation
    from hprofile import Profile, HotelProfile
    from recommend import RecommendType, Recommend

    print("I'm here!")
else:
    from benchmark.hotel.user import User
    from benchmark.hotel.search import Search, Geo, Rate
    from benchmark.hotel.reservation import Reservation
    from benchmark.hotel.profile import Profile, HotelProfile
    from benchmark.hotel.recommend import RecommendType, Recommend

from typing import List
from random import randrange
import os
import stateflow
import asyncio
from stateflow.client.fastapi.kafka import KafkaFastAPIClient, StateflowFailure
import json
import argparse


IS_KAFKA = bool(os.getenv("KAFKA"))
IS_PYFLINK = bool(os.getenv("PYFLINK"))

AMOUNT_OF_HOTELS = 80
AMOUNT_OF_USERS = 500
PARTITION_COUNT = os.getenv("NUM_PARTITIONS", AMOUNT_OF_HOTELS)
TIMEOUT = int(os.getenv("TIMEOUT", 5))

print(IS_KAFKA)
print(IS_PYFLINK)

if IS_KAFKA and False:
    producer_config = json.load(open(os.environ.get("PRODUCER_CONF"), "r"))
    consumer_config = json.load(open(os.environ.get("CONSUMER_CONF"), "r"))

    client = KafkaFastAPIClient(
        stateflow.init(),
        statefun_mode=True,
        producer_config=producer_config,
        consumer_config=consumer_config,
        timeout=TIMEOUT,
    )
elif IS_PYFLINK:
    producer_config = json.load(open(os.environ.get("PRODUCER_CONF"), "r"))
    consumer_config = json.load(open(os.environ.get("CONSUMER_CONF"), "r"))

    client = KafkaFastAPIClient(stateflow.init(), statefun_mode=False, timeout=TIMEOUT, producer_config=producer_config, consumer_config=consumer_config)
else:
    from stateflow.client.fastapi.aws_gateway import AWSGatewayFastAPIClient

    ADDRESS = os.environ.get("ADDRESS")
    client = AWSGatewayFastAPIClient(
        stateflow.init(), api_gateway_url=ADDRESS, timeout=TIMEOUT
    )
app = client.get_app()


def _get_partition() -> int:
    return randrange(0, PARTITION_COUNT)


async def check_availability_hotel(hotel_id: str, in_date, out_date):
    reservation: Reservation = await Reservation.by_key(hotel_id)
    is_available: bool = await reservation.check_availability(in_date, out_date, 1)

    return hotel_id, is_available


@app.get("/search")
async def search(lat: float, lon: float, in_date: str, out_date: str):
    try:
        # Here we select the 'partitioned services'.
        partition_id = _get_partition()
        search: Search = await Search.by_key(f"search-service-{partition_id}")
        geo: Geo = await Geo.by_key(f"geo-service-{partition_id}")
        rate: Rate = await Rate.by_key(f"rate-service-{partition_id}")
        profile: Profile = await Profile.by_key(f"profile-service-{partition_id}")

        # Find nearby hotels.
        nearby_hotels: List[str] = await search.nearby(lat, lon, geo, rate)

        # All available hotels.
        available_hotels: List[str] = []

        availability = asyncio.as_completed(
            [
                check_availability_hotel(hotel_id, in_date, out_date)
                for hotel_id in nearby_hotels
            ]
        )

        for fut in availability:
            hotel_id, is_available = await fut
            if is_available:
                available_hotels.append(hotel_id)

        profiles: List[HotelProfile] = await profile.get_profiles(available_hotels)
    except Exception:
        return "Internal server error"

    return profiles


@app.get("/recommend")
async def recommend(
    recommendation_type: RecommendType, lat: float = 0.0, lon: float = 0.0
):
    recommendation_type = recommendation_type

    # Here we select the 'partitioned services'.
    recommend: Recommend = await Recommend.by_key(
        f"recommend-service-{_get_partition()}"
    )
    profile: Profile = await Profile.by_key(f"profile-service-{_get_partition()}")

    # Get recommendations.
    recommendations: List[str] = await recommend.recommend(
        recommendation_type, {"lat": lat, "lon": lon}
    )

    print(f"Found recommendations {recommendations}")

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
    user: User = await User.by_key(username)

    # Login the user first.
    login_success: bool = await user.login(password)

    if not login_success:
        return "Can't reserve, login failed."

    # Get hotel reservation system (i.e. stateful function).
    reserve: Reservation = await Reservation.by_key(hotel_id)

    # Try to make the reservation.
    reserve_success: bool = await reserve.add_reservation(
        customer_name, in_date, out_date, amount_of_rooms
    )

    if reserve_success:
        return "Reserve successful!"
    else:
        return "Failed reserving, room is already booked."


@app.get("/login")
async def user(username: str, password: str):
    user: User = await User.by_key(username)

    # Login the user.
    login_success: bool = await user.login(password)

    return login_success


# INIT
@app.get("/init_create_users")
async def create_users():
    created = 0
    not_created = 0
    for f in asyncio.as_completed(
        [User(f"TUDelft_{i}", "random_password") for i in range(AMOUNT_OF_USERS)]
    ):

        try:
            user = await f
            if isinstance(user, StateflowFailure):
                not_created += 1
                print(user.error_msg)
            else:
                created += 1
        except StateflowFailure as exc:
            print(exc.error_msg)
            not_created += 1

    return {
        "created": created,
        "not_created": not_created,
        "total": created + not_created,
    }


@app.get("/init_create_hotels")
async def create_hotels():
    created = 0
    not_created = 0

    await Reservation("1", 200)
    await Reservation("2", 200)
    await Reservation("3", 200)

    hotel_four: Reservation = await Reservation("4", 200)

    if isinstance(hotel_four, StateflowFailure):
        hotel_four: Reservation = await Reservation.by_key("4")

    await Reservation("5", 200)
    await Reservation("6", 200)

    await hotel_four.add_reservation("Alice", "2015-04-09", "2015-04-10", 1)

    all_hotels = []
    for i in range(7, AMOUNT_OF_HOTELS + 1):

        max_capacity = 200

        if i % 3 == 1:
            max_capacity = 300
        elif i % 3 == 2:
            max_capacity = 250

        all_hotels.append(Reservation(str(i), max_capacity))

    for f in asyncio.as_completed(all_hotels):

        try:
            hotel = await f
            if isinstance(hotel, StateflowFailure):
                not_created += 1
                print(hotel.error_msg)
            else:
                created += 1
        except StateflowFailure as exc:
            print(exc.error_msg)
            not_created += 1

    return {
        "created": created + 6,
        "not_created": not_created,
        "total": created + not_created + 6,
    }


@app.get("/init_create_services")
async def create_services():
    created_geo = 0
    not_created_geo = 0

    for f in asyncio.as_completed(
        [Geo(f"geo-service-{i}", AMOUNT_OF_HOTELS) for i in range(PARTITION_COUNT)]
    ):
        try:
            geo = await f
            if isinstance(geo, StateflowFailure):
                not_created_geo += 1
                print(geo.error_msg)
            else:
                created_geo += 1
        except StateflowFailure as exc:
            print(exc.error_msg)
            not_created_geo += 1

    created_rate = 0
    not_created_rate = 0

    for f in asyncio.as_completed(
        [Rate(f"rate-service-{i}", AMOUNT_OF_HOTELS) for i in range(PARTITION_COUNT)]
    ):
        try:
            rate = await f
            if isinstance(rate, StateflowFailure):
                not_created_rate += 1
                print(rate.error_msg)
            else:
                created_rate += 1
        except StateflowFailure as exc:
            print(exc.error_msg)
            not_created_rate += 1

    created_search = 0
    not_created_search = 0

    for f in asyncio.as_completed(
        [Search(f"search-service-{i}") for i in range(PARTITION_COUNT)]
    ):
        try:
            search = await f
            if isinstance(search, StateflowFailure):
                not_created_search += 1
                print(search.error_msg)
            else:
                created_search += 1
        except StateflowFailure as exc:
            print(exc.error_msg)
            not_created_search += 1

    created_profile = 0
    not_created_profile = 0

    for f in asyncio.as_completed(
        [
            Profile(f"profile-service-{i}", AMOUNT_OF_HOTELS)
            for i in range(PARTITION_COUNT)
        ]
    ):
        try:
            profile = await f
            if isinstance(profile, StateflowFailure):
                not_created_profile += 1
                print(profile.error_msg)
            else:
                created_profile += 1
        except StateflowFailure as exc:
            print(exc.error_msg)
            not_created_profile += 1

    created_recommend = 0
    not_created_recommend = 0

    for f in asyncio.as_completed(
        [
            Recommend(f"recommend-service-{i}", AMOUNT_OF_HOTELS)
            for i in range(PARTITION_COUNT)
        ]
    ):
        try:
            recommend = await f
            if isinstance(recommend, StateflowFailure):
                not_created_recommend += 1
                print(recommend.error_msg)
            else:
                created_recommend += 1
        except StateflowFailure as exc:
            print(exc.error_msg)
            not_created_recommend += 1

    return {
        "created_geo": created_geo,
        "not_created_geo": not_created_geo,
        "total_geo": created_geo + not_created_geo,
        "created_rate": created_rate,
        "not_created_rate": not_created_rate,
        "total_rate": created_rate + not_created_rate,
        "created_profile": created_profile,
        "not_created_profile": not_created_profile,
        "total_profile": created_profile + not_created_profile,
        "created_search": created_search,
        "not_created_search": not_created_search,
        "total_search": created_search + not_created_search,
        "created_recommend": created_recommend,
        "not_created_recommend": not_created_recommend,
        "total_recommend": created_recommend + not_created_recommend,
        "total": created_geo
        + not_created_geo
        + created_rate
        + not_created_rate
        + created_profile
        + not_created_profile
        + created_search
        + not_created_search
        + created_recommend
        + not_created_recommend,
    }
