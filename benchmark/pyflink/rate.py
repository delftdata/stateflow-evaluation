import json
import stateflow
from dataclasses import dataclass
from typing import List


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


@stateflow.stateflow
class Rate:
    def __init__(self, rate_id: str, amount_of_hotels: int):
        self.rate_id = rate_id
        self.rate_plans: List[RatePlan] = []

        self._load_data(amount_of_hotels)

    def _load_data(self, amount_of_hotels):
        data = json.load(open("./data/inventory.json"))
        for d in data:
            self.rate_plans.append(
                RatePlan(
                    d["hotelId"],
                    d["code"],
                    d["inDate"],
                    d["outDate"],
                    RoomType(
                        d["roomType"]["bookableRate"],
                        d["roomType"]["code"],
                        d["roomType"]["description"],
                        d["roomType"]["totalRate"],
                        d["roomType"]["totalRateInclusive"],
                    ),
                )
            )

        for hotel_id in range(4, amount_of_hotels + 1):
            if hotel_id % 3 == 0:
                end_date = "2015-04-"
                rate = 109.00
                rate_inc = 123.17

                if hotel_id % 2 == 0:
                    end_date += "17"
                else:
                    end_date += "24"

                if hotel_id % 5 == 1:
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

                self.rate_plans.append(
                    RatePlan(
                        str(hotel_id),
                        "RACK",
                        "2015-04-09",
                        end_date,
                        RoomType(rate, "KNG", "King sized bed", rate, rate_inc),
                    )
                )

    def get_rates(self, hotel_ids: List[str]) -> List[RatePlan]:
        # Deathstar benchmark mentions getting rates for a specific date range.
        # In practice, they just return all rates matching a hotel id.
        return [plan for plan in self.rate_plans if plan.hotelId in hotel_ids]

    def __key__(self):
        return self.rate_id
