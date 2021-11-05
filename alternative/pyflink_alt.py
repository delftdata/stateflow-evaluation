from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.functions import (
    KeyedProcessFunction,
    RuntimeContext,
ProcessFunction,
    ValueStateDescriptor,
    ValueState,
)
import json
from enum import Enum
from math import radians, cos, sin, asin, sqrt
import sys
import datetime
from dataclasses import dataclass
from typing import List

# 25 lines
class UserOperator(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("state", Types.BYTE())
        self.state: ValueState = runtime_context.get_state(descriptor)

    def process_element(self, event, ctx: KeyedProcessFunction.Context):
        user = json.loads(self.state.value())
        username = event["username"]
        password = event["password"]

        if event["type"] == "CREATE_USER":
            user_item = {username: username, password: password}
            self.state.update(json.dumps(user_item))

            yield {"message": "created a user!"}
        elif event["type"] == "LOGIN_USER":
            if user is None:
                yield {"message": "user not found"}
            else:
                yield {"message": user["password"] == password}


env: StreamExecutionEnvironment = StreamExecutionEnvironment.get_execution_environment()
env.from_source(FlinkKafkaConsumer()).map(lambda x: json.loads(x)).key_by(
    lambda x: x["username"]
).process(UserOperator()).sink_to(FlinkKafkaProducer())

env.run()

# 22 LOC, 15 NAP
class SearchOperator(ProcessFunction):
    def process_element(self, event, ctx: ProcessFunction.Context):
        event_type = event["type"]

        if event_type == "SEARCH_REQUEST":  # Start querying geo service
            lat = event["lat"]
            lon = event["lon"]
            payload = json.dumps({"lat": lat, "lon": lon, "event_type": "SEARCH_REQUEST", "route": "geo"})
            return payload
        elif event_type == "GEO_RESPONSE":  # Response from geo service, start querying rate service
            nearby_hotels: List[str] = event["geo_results"]
            payload = json.dumps({"hotel_ids": nearby_hotels, "event_type": "SEARCH_REQUEST", "route": "rate"})
            return payload
        elif event_type == "RATE_RESPONSE":
            rate_plans = event["rate_results"]
            payload = json.dumps({"results": rate_plans, "route": "client"})
            return payload


env: StreamExecutionEnvironment = StreamExecutionEnvironment.get_execution_environment()
search_result = env.from_source(FlinkKafkaConsumer()).process(SearchOperator())

# For each output, we have to produce to a different Kafka topic
search_result.filter(lambda x: x["route"] == "geo").sink_to(FlinkKafkaProducer())
search_result.filter(lambda x: x["route"] == "client").sink_to(FlinkKafkaProducer())
search_result.filter(lambda x: x["route"] == "rate").sink_to(FlinkKafkaProducer())

env.run()

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


# 39 LOC, 17 NAP
class GeoOperator(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("state", Types.BYTE())
        self.state: ValueState = runtime_context.get_state(descriptor)

    def process_element(self, event, ctx: KeyedProcessFunction.Context):
        event_type = event["type"]
        lat = event["lat"]
        lon = event["lon"]

        geo_points = json.loads(self.state.value())
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

        if event_type == "SEARCH_REQUEST":  # Start querying geo service
            payload = json.dumps({"geo_results": geo_results, "event_type": "GEO_RESPONSE", "route": "geo"})
            return payload
        else:
            payload = json.dumps({"geo_results": geo_results, "route": "client"})
            return payload

env: StreamExecutionEnvironment = StreamExecutionEnvironment.get_execution_environment()
geo_result = env.from_source(FlinkKafkaConsumer()).map(lambda x: json.loads(x)).key_by(
    lambda x: x["geo_id"]
).process(GeoOperator())

# For each output, we have to produce to a different Kafka topic
geo_result.filter(lambda x: x["route"] == "search").sink_to(FlinkKafkaProducer())
geo_result.filter(lambda x: x["route"] == "client").sink_to(FlinkKafkaProducer())

env.run()

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

# 37 loc, 17 NAC
class ProfileOperator(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("state", Types.BYTE())
        self.state: ValueState = runtime_context.get_state(descriptor)

    def process_element(self, event, ctx: KeyedProcessFunction.Context):
        hotel_ids = event["hotel_ids"]

        hotels_raw = json.loads(self.state.value())
        profiles: List[HotelProfile] = []

        for h_ser in hotels_raw.items():
            h = json.loads(h_ser)
            profiles.append(HotelProfile(h["id"], h["name"], h["phoneNumber"], h["description"],
                                         Address(h["streetNumber"], h["streetName"], h["city"],
                                                 h["state"], h["country"], h["postalCode"], h["lat"], h["lon"])))

        hotels = [hotel for hotel in profiles if hotel.id in hotel_ids]

        return hotels

env: StreamExecutionEnvironment = StreamExecutionEnvironment.get_execution_environment()
profile_result = env.from_source(FlinkKafkaConsumer()).map(lambda x: json.loads(x)).key_by(
    lambda x: x["profile_id"]
).process(ProfileOperator()).sink_to(FlinkKafkaProducer())

env.execute()

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

# 43 LOC, 22 NAC
class RateOperator(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("state", Types.BYTE())
        self.state: ValueState = runtime_context.get_state(descriptor)

    def process_element(self, event, ctx: KeyedProcessFunction.Context):
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

        if event_type == "SEARCH_REQUEST":  # Start querying geo service
            payload = json.dumps({"rate_results": hotels, "event_type": "RATE_RESPONSE", "route": "search"})
            return payload
        else:
            payload = json.dumps({"rate_results": hotels, "route": "client"})
            return payload

env: StreamExecutionEnvironment = StreamExecutionEnvironment.get_execution_environment()
rate_result = env.from_source(FlinkKafkaConsumer()).map(lambda x: json.loads(x)).key_by(
    lambda x: x["rate_id"]
).process(RateOperator())

# For each output, we have to produce to a different Kafka topic
rate_result.filter(lambda x: x["route"] == "search").sink_to(FlinkKafkaProducer())
rate_result.filter(lambda x: x["route"] == "client").sink_to(FlinkKafkaProducer())

env.execute()


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

#54 LOC, 10NAP
class RecommendOperator(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("state", Types.BYTE())
        self.state: ValueState = runtime_context.get_state(descriptor)

    def process_element(self, event, ctx: KeyedProcessFunction.Context):
        recommend_params = event["recommend_params"]
        recommend_type = RecommendType.value(event["recommend_type"])
        hotel_ids = event["hotel_ids"]

        hotels = [hotel for hotel in self.state.value().recommend if hotel.hotelId in hotel_ids]
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

        return reply

env: StreamExecutionEnvironment = StreamExecutionEnvironment.get_execution_environment()
recommend_result = env.from_source(FlinkKafkaConsumer()).map(lambda x: json.loads(x)).key_by(
    lambda x: x["recommend_id"]
).process(RecommendOperator()).sink_to(FlinkKafkaProducer())

env.execute()

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

# 61 LOC, 21 NAC
class ReserveOperator(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("state", Types.BYTE())
        self.state: ValueState = runtime_context.get_state(descriptor)

    def process_element(self, event, ctx: KeyedProcessFunction.Context):
        event_type = event["event_type"]

        h = json.loads(self.state.value())

        hotel_reservations: List[HotelReservation] = []
        max_capacity = h["max_capacity"]

        for r in h["reservations"]:
            hotel_reservations.append(r["customerId"], r["inDate"], r["outDate"], r["numberOfRooms"])

        if event_type == "AVAILABILITY":
            return {"message": check_availability(hotel_reservations, max_capacity, event["in_date"], event["out_date"],
                                                                     event["number_of_rooms"])}
        elif event_type == "RESERVE_ROOM":
            if not check_availability(hotel_reservations, max_capacity,
                                      event["in_date"], event["out_date"], event["number_of_rooms"]):
                return {'message': False}

            in_date = datetime.strptime(event["in_date"], "%Y-%m-%d")
            out_date = datetime.strptime(event["out_date"], "%Y-%m-%d")

            hotel_reservations.append(
                HotelReservation(event["customer_name"], in_date, out_date, event["number_of_rooms"]))
            reservations = []
            for r in hotel_reservations:
                reservations.append({
                    "customerId": r.customerId,
                    "inDate": r.inDate,
                    "outDate": r.outDate,
                    "number_of_rooms": r.numberOfRooms
                })

            self.state.update(json.dumps({
                'hotel_id': ctx.address.id,
                'max_capacity': max_capacity,
                'reservations': reservations
            }))

            return {'message': True}


env: StreamExecutionEnvironment = StreamExecutionEnvironment.get_execution_environment()
reserve_result = env.from_source(FlinkKafkaConsumer()).map(lambda x: json.loads(x)).key_by(
    lambda x: x["hotel_id"]
).process(ReserveOperator()).sink_to(FlinkKafkaProducer())

env.execute()