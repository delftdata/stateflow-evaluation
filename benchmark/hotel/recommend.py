import sys

import stateflow
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
import json
from math import radians, cos, sin, asin, sqrt


@dataclass
class HotelRecommend:
    hotelId: str
    lat: float
    lon: float
    rate: float
    price: float


class RecommendType(Enum):
    DISTANCE = 1
    RATE = 2
    PRICE = 3


@stateflow.stateflow
class Recommend:
    def __init__(self, recommend_id: str, amount_of_hotels: int):
        self.recommend_id = recommend_id
        self.hotels: List[HotelRecommend] = []

        self._load_data(amount_of_hotels)

    def _load_data(self, amount_of_hotels):
        # Just like Deathstar, we don't use a data file for this one
        self.hotels.append(HotelRecommend("1", 37.7867, -122.4112, 109.00, 150.00))
        self.hotels.append(HotelRecommend("2", 37.7854, -122.4005, 139.00, 120.00))
        self.hotels.append(HotelRecommend("3", 37.7834, -122.4071, 109.00, 190.00))
        self.hotels.append(HotelRecommend("4", 37.7936, -122.3930, 129.00, 160.00))
        self.hotels.append(HotelRecommend("5", 37.7831, -122.4181, 119.00, 140.00))
        self.hotels.append(HotelRecommend("6", 37.7863, -122.4015, 149.00, 200.00))

        for hotel_id in range(7, amount_of_hotels + 1):
            lat = 37.7835 + float(hotel_id) / 500.0 * 3
            lon = -122.41 + float(hotel_id) / 500.0 * 4

            rate = 135.00
            rate_inc = 179.00

            if hotel_id % 3 == 0:
                if hotel_id % 5 == 0:
                    rate = 109.00
                    rate_inc = 123.17
                elif hotel_id % 5 == 1:
                    rate = 120.00
                    rate_inc = 140.00
                elif hotel_id % 5 == 2:
                    rate = 124.00
                    rate_inc = 144.00
                elif hotel_id % 5 == 3:
                    rate = 132.00
                    rate_inc = 158.00
                elif hotel_id % 5 == 4:
                    rate = 232.00
                    rate_inc = 258.00

            self.hotels.append(HotelRecommend(str(hotel_id), lat, lon, rate, rate_inc))

    def _dist(self, lat1, long1, lat2, long2):
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

    def recommend(
        self, recommend_type: RecommendType, recommend_params: Dict
    ) -> List[str]:
        if recommend_type == RecommendType.DISTANCE:
            lat: float = recommend_params["lat"]
            lon: float = recommend_params["lon"]

            min_dist: float = sys.float_info.max
            return_hotels: List[str] = []
            for hotel in self.hotels:
                dist: float = self._dist(lat, lon, hotel.lat, hotel.lon)

                if dist < min_dist:
                    min_dist = dist

            for hotel in self.hotels:
                dist: float = self._dist(lat, lon, hotel.lat, hotel.lon)

                if dist == min_dist:
                    return_hotels.append(hotel.hotelId)
            return return_hotels

        elif recommend_type == RecommendType.RATE:
            max_rate: float = 0

            for hotel in self.hotels:
                rate: int = hotel.rate

                if rate > max_rate:
                    max_rate = rate

            return [hotel.hotelId for hotel in self.hotels if hotel.rate == max_rate]
        elif recommend_type == RecommendType.PRICE:
            min_price: float = sys.float_info.max

            for hotel in self.hotels:
                if hotel.price < min_price:
                    min_price = hotel.price

            return [hotel.hotelId for hotel in self.hotels if hotel.price == min_price]

    def __key__(self):
        return self.recommend_id
