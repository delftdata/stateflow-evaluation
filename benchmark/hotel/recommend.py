import stateflow
from dataclasses import dataclass
from typing import List
import json


@dataclass
class HotelRecommend:
    hotelId: str
    lat: float
    lon: float
    rate: float
    price: float


@stateflow.stateflow
class Recommend:
    def __init__(self, recommend_id: str, amount_of_hotels: int):
        self.recommend_id = recommend_id
        self.hotels: List[HotelRecommend] = []

    def _load_data(self, amount_of_hotels):
        # Just like Deathstar, we don't use a data file for this one
        self.hotels.append(HotelRecommend("1", 37.7867, -122.4112, 109.00, 150.00))
        self.hotels.append(HotelRecommend("2", 37.7854, -122.4005, 139.00, 120.00))
        self.hotels.append(HotelRecommend("3", 37.7834, -122.4071, 109.00, 190.00))
        self.hotels.append(HotelRecommend("4", 37.7936, -122.3930, 129.00, 160.00))
        self.hotels.append(HotelRecommend("5", 37.7831, -122.4181, 119.00, 140.00))
        self.hotels.append(HotelRecommend("6", 37.7863, -122.4015, 149.00, 200.00))

    def __key__(self):
        return self.recommend_id
