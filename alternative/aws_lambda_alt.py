import boto3
from botocore.exceptions import ClientError
import json
from typing import List
from math import radians, cos, sin, asin, sqrt
from dataclasses import dataclass
from enum import Enum
import sys
import datetime

dynamodb = boto3.client("dynamodb")
table = dynamodb.Table("users")
# 17 lines, 11 non-appl
def user_handler(event, context):
    username = event["username"]
    password = event["password"]
    if event["type"] == "CREATE_USER":
        user_item = {username: username, password: password}
        dynamodb.put_item(TableName="users", Item=json.dump(user_item))

        return {"message": "created a user!"}
    elif event["type"] == "LOGIN_USER":
        try:
            response = table.get_item(Key={"username": username})
        except ClientError as e:
            return {"message": "user not found"}
        else:
            user = json.loads(response["Item"])
            return {"message": user["password"] == password}


# 13 lines, 8 non-appl
client = boto3.client("lambda")


def search_handler(event, context):
    lat = event["lat"]
    lon = event["lon"]

    payload = json.dumps({"lat": lat, "lon": lon})
    geo_response = client.invoke(
        FunctionName="geo", InvocationType="Event", Payload=payload
    )
    geo_payload = json.loads(geo_response.read())
    nearby_hotels: List[str] = geo_payload("hotel_ids")

    payload = json.dumps({"hotel_ids": nearby_hotels})
    rate_response = client.invoke(
        FunctionName="rate", InvocationType="Event", Payload=payload
    )
    rate_payload = json.loads(rate_response.read())
    rate_plans: List[str] = rate_payload.get("hotel_ids")

    return {"message": rate_plans}


MAX_SEARCH_RESULTS = 5
MAX_SEARCH_RADIUS = 10
dynamodb = boto3.client("dynamodb")
table = dynamodb.Table("geo")


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


# 31 lines, 10 NAP
def geo_handler(event, context):
    lat = event["lat"]
    lon = event["lon"]

    try:
        response = table.get_item(Key={"geo_points": "geo_points"})  # Global key
    except ClientError as e:
        return {"message": "geo points not found"}
    else:
        geo_points_raw = json.loads(response["Item"])
        geo_points = []
        for geo_point in geo_points_raw:
            geo_points.append(
                GeoPoint(geo_point["hotelId"], geo_point["lat"], geo_point["lon"])
            )

    all_distances = [
        (point.hotelId, _dist(point.lat, point.lon, float(lat), float(lon)))
        for point in geo_points
    ]
    # This is quite inefficient for large lists, but we can improve it later.
    all_distances = [dist for dist in all_distances if dist[1] <= MAX_SEARCH_RADIUS]
    all_distances.sort(key=lambda x: x[1], reverse=False)

    limit_distances = all_distances[0:MAX_SEARCH_RESULTS]

    return {"message": list([x[0] for x in limit_distances])}


dynamodb = boto3.client("dynamodb")
table = dynamodb.Table("profile")


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


# 33 LOC, 12 NAP
def profile_handler(event, context):
    hotel_ids = event["hotel_ids"]

    try:
        response = table.batch_get_item(Keys={"hotels": hotel_ids})
    except ClientError as e:
        return {"message": "hotels not found"}
    else:
        hotels: List[HotelProfile] = []

        for h_ser in response.items():
            h = json.loads(h_ser)
            hotels.append(
                HotelProfile(
                    h["id"],
                    h["name"],
                    h["phoneNumber"],
                    h["description"],
                    Address(
                        h["streetNumber"],
                        h["streetName"],
                        h["city"],
                        h["state"],
                        h["country"],
                        h["postalCode"],
                        h["lat"],
                        h["lon"],
                    ),
                )
            )
        return {"message": hotels}


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


dynamodb = boto3.client("dynamodb")
table = dynamodb.Table("rate")

# 30 LOC, 13 NAP
def rate_handler(event, context):
    hotel_ids = event["hotel_ids"]

    try:
        response = table.batch_get_item(Keys={"hotels": hotel_ids})
    except ClientError as e:
        return {"message": "hotels not found"}
    else:
        hotels: List[RatePlan] = []

        for h_ser in response.items():
            h = json.loads(h_ser)
            hotels.append(
                RatePlan(
                    h["hotelId"],
                    h["code"],
                    h["inDate"],
                    h["outDate"],
                    RoomType(
                        h["bookableRate"],
                        h["code"],
                        h["description"],
                        h["totalRate"],
                        h["totalRateInclusive"],
                    ),
                )
            )
        return {"message": hotels}


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


dynamodb = boto3.client("dynamodb")
table = dynamodb.Table("recommend")

# 54 LOC, 14 NAC
def recommend_handler(event, context):
    recommend_params = event["recommend_params"]
    recommend_type = RecommendType.value(event["recommend_type"])
    hotel_ids = event["hotel_ids"]

    try:
        response = table.batch_get_item(Keys={"hotels": hotel_ids})
    except ClientError as e:
        return {"message": "hotels not found"}
    else:
        hotels: List[HotelProfile] = []

        for h_ser in response.items():
            h = json.loads(h_ser)
            hotels.append(h["hotelId"], h["lat"], h["lon"], h["rate"], h["price"])

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
        return {"message": return_hotels}

    elif recommend_type == RecommendType.RATE:
        # Hotels with maximum rate.
        max_rate: float = 0

        for hotel in hotels:
            rate: int = hotel.rate

            if rate > max_rate:
                max_rate = rate

        return {
            "message": [hotel.hotelId for hotel in hotels if hotel.rate == max_rate]
        }
    elif recommend_type == RecommendType.PRICE:
        # Hotels with minimal price.
        min_price: float = sys.float_info.max

        for hotel in hotels:
            if hotel.price < min_price:
                min_price = hotel.price

        return {
            "message": [hotel.hotelId for hotel in hotels if hotel.price == min_price]
        }


@dataclass
class HotelReservation:

    customerId: str
    inDate: datetime
    outDate: datetime
    numberOfRooms: int

    def has_date_conflict(self, in_date: datetime, out_date: datetime) -> bool:
        return in_date <= self.outDate and out_date >= self.inDate


def check_availability(
    reservations: List[HotelReservation],
    max_capacity: int,
    in_date: str,
    out_date: str,
    number_of_rooms: int,
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


dynamodb = boto3.client("dynamodb")
table = dynamodb.Table("hotel")

# 60 LOC, 29 NAP
def reserve_handler(event, context):
    hotel_id = event["hotel_id"]

    # Load hotel
    try:
        response = table.get_item(Keys={"hotel": hotel_id})
    except ClientError as e:
        return {"message": "hotel not found"}
    else:
        hotel_reservations: List[HotelReservation] = []
        h = json.loads(response["Item"])
        max_capacity = h["max_capacity"]

        for r in h["reservations"]:
            hotel_reservations.append(
                r["customerId"], r["inDate"], r["outDate"], r["numberOfRooms"]
            )

    if event["type"] == "AVAILABILITY":
        return {
            "message": check_availability(
                hotel_reservations,
                max_capacity,
                event["in_date"],
                event["out_date"],
                event["number_of_rooms"],
            )
        }
    elif event["type"] == "RESERVE_ROOM":
        if not check_availability(
            hotel_reservations,
            max_capacity,
            event["in_date"],
            event["out_date"],
            event["number_of_rooms"],
        ):
            return {"message": False}

        in_date = datetime.strptime(event["in_date"], "%Y-%m-%d")
        out_date = datetime.strptime(event["out_date"], "%Y-%m-%d")

        hotel_reservations.append(
            HotelReservation(
                event["customer_name"], in_date, out_date, event["number_of_rooms"]
            )
        )
        reservations = []
        for r in hotel_reservations:
            reservations.append(
                {
                    "customerId": r.customerId,
                    "inDate": r.inDate,
                    "outDate": r.outDate,
                    "number_of_rooms": r.numberOfRooms,
                }
            )
        table.put_item(
            Item={
                "hotel_id": hotel_id,
                "max_capacity": max_capacity,
                "reservations": reservations,
            }
        )

        return {"message": True}
