from statefun import *
import json
from typing import List
from dataclasses import dataclass
from enum import Enum
from math import radians, cos, sin, asin, sqrt
import sys
import datetime

functions = StatefulFunctions()
@functions.bind(typename='nl.tudelft.benchmark/user', specs=[ValueSpec(name='user', type=StringType)])
async def user_handler(ctx: Context, message: Message):
    user_state = ctx.storage.user

    event = json.loads(message.event)
    username = event["username"]
    password = event["password"]

    reply = None

    if event["type"] == "CREATE_USER":
        user_item = {username: username, password: password}
        context.storage.user = json.dumps(user_item)

        reply = {"message": "created a user!"}
    elif event["type"] == "LOGIN_USER":
        if user_state is None:
            reply = {"message": "user not found"}
        else:
            user = json.loads(user_state)
            if user["password"] == password:
                reply = {"message": False}
            else:
                reply = {"message": True}

    context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                             topic='reply',
                                             key=username,
                                             value=reply))


# 20 lines, 11 NAP
functions = StatefulFunctions()
@functions.bind(typename='nl.tudelft.benchmark/search', specs=[])
async def search_handler(ctx: Context, message: Message):
    event = json.loads(message.event)
    event_type = event["type"]

    if event_type == "SEARCH_REQUEST": # Start querying geo service
        lat = event["lat"]
        lon = event["lon"]
        payload = json.dumps({"lat": lat, "lon": lon, "event_type": "SEARCH_REQUEST"})
        ctx.send(message_builder(target_typename='nl.tudelft.benchmark/geo', target_id="geo", str_value=payload))
    elif event_type == "GEO_RESPONSE": # Response from geo service, start querying rate service
        nearby_hotels: List[str] = event["geo_results"]
        payload = json.dumps({"hotel_ids": nearby_hotels, "event_type": "SEARCH_REQUEST"})
        ctx.send(message_builder(target_typename='nl.tudelft.benchmark/rate', target_id="rate", str_value=payload))
    elif event_type == "RATE_RESPONSE":
        rate_plans = event["rate_results"]
        context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                                 topic='reply',
                                                 key="",
                                                 value=rate_plans))

MAX_SEARCH_RESULTS = 5
MAX_SEARCH_RADIUS = 10

@dataclass
class GeoPoint:
    hotelId: str
    lat: float
    lon: float

def _dist(lat1, long1, lat2, long2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    Taken from: https://medium.com/analytics-vidhya/finding-nearest-pair-of-latitude-and-longitude-match-using-python-ce50d62af546
    """
    # convert decimal degrees to radians
    lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
    # haversine formula
    dlon = long2 - long1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km

# 34 lines, 12 NAP
functions = StatefulFunctions()
@functions.bind(typename='nl.tudelft.benchmark/geo', specs=[ValueSpec(name='geo', type=StringType)])
async def geo_handler(ctx: Context, message: Message):
    event = json.loads(message.event)
    event_type = event["type"]
    lat = event["lat"]
    lon = event["lon"]

    geo_points = json.loads(ctx.storage.geo)
    all_distances = [
        (point.hotelId, _dist(point.lat, point.lon, float(lat), float(lon)))
        for point in geo_points
    ]

    all_distances = [
        dist for dist in all_distances if dist[1] <= MAX_SEARCH_RADIUS
    ]
    all_distances.sort(key=lambda x: x[1], reverse=False)

    limit_distances = all_distances[0: MAX_SEARCH_RESULTS]
    geo_results = list([x[0] for x in limit_distances])


    if event_type == "SEARCH_REQUEST": # Start querying geo service
        payload = json.dumps({"geo_results": geo_results, "event_type": "GEO_RESPONSE"})
        ctx.send(message_builder(target_typename='nl.tudelft.benchmark/search', target_id="search", str_value=payload))
    else:
        payload = json.dumps({"geo_results": geo_results})
        context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                                 topic='reply',
                                                 key="",
                                                 value=payload))

@dataclass
class Address:

    streetNumber: str
    streetName: str
    city: str
    state: str
    country: str
    postalCode: str
    lat: float
    lon: float

@dataclass
class HotelProfile:
    id: str
    name: str
    phoneNumber: str
    description: str
    address: Address

# 35 lines, 13 NAP
functions = StatefulFunctions()
@functions.bind(typename='nl.tudelft.benchmark/profile', specs=[ValueSpec(name='profile', type=StringType)])
async def profile_handler(ctx: Context, message: Message):
    event = json.loads(message.event)
    hotel_ids = event["hotel_ids"]

    hotels_raw = json.loads(ctx.storage.hotels)
    profiles: List[HotelProfile] = []

    for h_ser in hotels_raw.items():
        h = json.loads(h_ser)
        profiles.append(HotelProfile(h["id"], h["name"], h["phoneNumber"], h["description"],
                                   Address(h["streetNumber"], h["streetName"], h["city"],
                                           h["state"], h["country"], h["postalCode"], h["lat"], h["lon"])))

    hotels = [hotel for hotel in profiles if hotel.id in hotel_ids]

    context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                             topic='reply',
                                             key="",
                                             value=hotels))


@dataclass
class RoomType:
    bookableRate: int
    code: str
    description: str
    totalRate: int
    totalRateInclusive: int


@dataclass
class RatePlan:

    hotelId: str
    code: str
    inDate: str
    outDate: str
    roomType: RoomType

# 36 lines, 18 NAP
functions = StatefulFunctions()
@functions.bind(typename='nl.tudelft.benchmark/rate', specs=[ValueSpec(name='rate', type=StringType)])
async def rate_handler(ctx: Context, message: Message):
    event = json.loads(message.event)
    event_type = event["event_type"]
    hotel_ids = event["hotel_ids"]

    hotels_raw = json.loads(ctx.storage.rate)
    rates: List[RatePlan] = []

    for h_ser in hotels_raw.items():
        h = json.loads(h_ser)
        rates.append(RatePlan(h["hotelId"], h["code"], h["inDate"], h["outDate"],
                               RoomType(h["bookableRate"], h["code"], h["description"],
                                        h["totalRate"], h["totalRateInclusive"])))

    hotels = [hotel for hotel in rates if hotel.hotelId in hotel_ids]

    if event_type == "SEARCH_REQUEST": # Start querying geo service
        payload = json.dumps({"rate_results": hotels, "event_type": "RATE_RESPONSE"})
        ctx.send(message_builder(target_typename='nl.tudelft.benchmark/search', target_id="search", str_value=payload))
    else:
        context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                             topic='reply',
                                             key="",
                                             value=hotels))


@dataclass
class HotelRecommend:
    hotelId: str
    lat: float
    lon: float
    rate: float
    price: float


class RecommendType(Enum):
    DISTANCE = "DISTANCE"
    RATE = "RATE"
    PRICE = "PRICE"

# 53 LOC, 9 NAP
functions = StatefulFunctions()
@functions.bind(typename='nl.tudelft.benchmark/recommend', specs=[ValueSpec(name='recommend', type=StringType)])
async def recommend_handler(ctx: Context, message: Message):
    event = json.loads(message.event)
    recommend_params = event["recommend_params"]
    recommend_type = RecommendType.value(event["recommend_type"])
    hotel_ids = event["hotel_ids"]

    hotels = [hotel for hotel in ctx.storage.recommend if hotel.hotelId in hotel_ids]
    reply = None
    if recommend_type == RecommendType.DISTANCE:
        # Hotels with minimal distance.

        lat: float = recommend_params["lat"]
        lon: float = recommend_params["lon"]

        min_dist: float = sys.float_info.max
        return_hotels: List[str] = []
        for hotel in hotels:
            dist: float = _dist(lat, lon, hotel.lat, hotel.lon)

            if dist < min_dist:
                min_dist = dist

        for hotel in hotels:
            dist: float = _dist(lat, lon, hotel.lat, hotel.lon)

            if dist == min_dist:
                return_hotels.append(hotel.hotelId)
        reply = return_hotels

    elif recommend_type == RecommendType.RATE:
        # Hotels with maximum rate.
        max_rate: float = 0

        for hotel in hotels:
            rate: int = hotel.rate

            if rate > max_rate:
                max_rate = rate

        reply = [hotel.hotelId for hotel in hotels if hotel.rate == max_rate]
    elif recommend_type == RecommendType.PRICE:
        # Hotels with minimal price.
        min_price: float = sys.float_info.max

        for hotel in hotels:
            if hotel.price < min_price:
                min_price = hotel.price

        reply = [hotel.hotelId for hotel in hotels if hotel.price == min_price]

    context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                             topic='reply',
                                             key="",
                                             value=json.dumps(reply)))

@dataclass
class HotelReservation:

    customerId: str
    inDate: datetime
    outDate: datetime
    numberOfRooms: int

    def has_date_conflict(self, in_date: datetime, out_date: datetime) -> bool:
        return in_date <= self.outDate and out_date >= self.inDate

def check_availability(
        reservations: List[HotelReservation], max_capacity: int, in_date: str, out_date: str, number_of_rooms: int
) -> bool:
    in_date = datetime.strptime(in_date, "%Y-%m-%d")
    out_date = datetime.strptime(out_date, "%Y-%m-%d")

    current_capacity: int = sum(
        [
            reserve.numberOfRooms
            for reserve in reservations
            if reserve.has_date_conflict(in_date, out_date)
        ]
    )
    return not (current_capacity + number_of_rooms > max_capacity)

# 66 LOC, 25 NAP
functions = StatefulFunctions()
@functions.bind(typename='nl.tudelft.benchmark/reservation', specs=[ValueSpec(name='reservation', type=StringType)])
async def reserve_handler(ctx: Context, message: Message):
    event = json.loads(message.event)
    event_type = event["event_type"]

    h = json.loads(ctx.storage.reservation)

    hotel_reservations: List[HotelReservation] = []
    max_capacity = h["max_capacity"]

    for r in h["reservations"]:
        hotel_reservations.append(r["customerId"], r["inDate"], r["outDate"], r["numberOfRooms"])

    if event_type == "AVAILABILITY":
        context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                                 topic='reply',
                                                 key="",
                                                 value={"message":
                                                            check_availability(hotel_reservations, max_capacity,
                                                        event["in_date"], event["out_date"], event["number_of_rooms"])}))
        return
    elif event_type== "RESERVE_ROOM":
        if not check_availability(hotel_reservations, max_capacity,
                                  event["in_date"], event["out_date"], event["number_of_rooms"]):
            context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                                     topic='reply',
                                                     key="",
                                                     value={"message": False}))
            return

        in_date = datetime.strptime(event["in_date"], "%Y-%m-%d")
        out_date = datetime.strptime(event["out_date"], "%Y-%m-%d")

        hotel_reservations.append(HotelReservation(event["customer_name"], in_date, out_date, event["number_of_rooms"]))
        reservations = []
        for r in hotel_reservations:
            reservations.append({
                "customerId": r.customerId,
                "inDate": r.inDate,
                "outDate": r.outDate,
                "number_of_rooms": r.numberOfRooms
            })

        ctx.storage.reservation = json.dumps({
                'hotel_id': ctx.address.id,
                'max_capacity': max_capacity,
                'reservations': reservations
            })

        context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                                 topic='reply',
                                                 key="",
                                                 value={"message": True}))