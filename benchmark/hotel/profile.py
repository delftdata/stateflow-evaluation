import stateflow
from dataclasses import dataclass
from typing import List
import json


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


@stateflow.stateflow
class Profile:
    def __init__(self, profile_id: str, amount_of_hotels: int):
        self.profile_id = profile_id
        self.profiles: List[HotelProfile] = []

        self._load_data(amount_of_hotels)

    def _load_data(self, amount_of_hotels: int):
        data = json.load(open("./hotel/data/hotels.json"))
        for d in data:
            self.profiles.append(
                HotelProfile(
                    d["id"],
                    d["name"],
                    d["phoneNumber"],
                    d["description"],
                    Address(
                        d["address"]["streetNumber"],
                        d["address"]["streetName"],
                        d["address"]["city"],
                        d["address"]["state"],
                        d["address"]["country"],
                        d["address"]["postalCode"],
                        d["address"]["lat"],
                        d["address"]["lon"],
                    ),
                )
            )

        for hotel_id in range(7, amount_of_hotels + 1):
            lat = 37.7835 + float(hotel_id) / 500.0 * 3
            lon = -122.41 + float(hotel_id) / 500.0 * 4

            phone_num = "(415) 284-40" + str(hotel_id)

            self.profiles.append(
                HotelProfile(
                    str(hotel_id),
                    "St. Regis San Francisco",
                    phone_num,
                    "St. Regis Museum Tower is a 42-story, "
                    + "484 ft skyscraper in the South of Market district of San Francisco, "
                    + "California, adjacent to Yerba Buena Gardens, Moscone Center, "
                    + "PacBell Building and the San Francisco Museum of Modern Art.",
                    Address(
                        "125",
                        "3rd St",
                        "San Francisco",
                        "CA",
                        "United States",
                        "94109",
                        lat,
                        lon,
                    ),
                )
            )

    def get_profiles(self, hotel_ids: List[str]) -> List[HotelProfile]:
        return list([hotel for hotel in self.profiles if hotel.id in hotel_ids])

    def __key__(self):
        return self.profile_id
