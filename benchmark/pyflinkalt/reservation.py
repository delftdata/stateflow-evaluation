import stateflow
from typing import List
from dataclasses import dataclass
import time
from datetime import datetime


@dataclass
class HotelReservation:

    customerId: str
    inDate: datetime
    outDate: datetime
    numberOfRooms: int

    def has_date_conflict(self, in_date: datetime, out_date: datetime) -> bool:
        return in_date <= self.outDate and out_date >= self.inDate


@stateflow.stateflow
class Reservation:
    def __init__(self, hotel_id: str, max_capacity: int):
        self.hotel_id = hotel_id
        self.max_capacity = max_capacity
        self.reservations: List[HotelReservation] = []

    def add_reservation(
        self, customer_name: str, in_date: str, out_date: str, number_of_rooms: int
    ) -> bool:
        if not self.check_availability(in_date, out_date, number_of_rooms):
            return False

        in_date = datetime.strptime(in_date, "%Y-%m-%d")
        out_date = datetime.strptime(out_date, "%Y-%m-%d")

        self.reservations = self.reservations + [
            HotelReservation(customer_name, in_date, out_date, number_of_rooms)
        ]

        return True

    def check_availability(
        self, in_date: str, out_date: str, number_of_rooms: int
    ) -> bool:
        in_date = datetime.strptime(in_date, "%Y-%m-%d")
        out_date = datetime.strptime(out_date, "%Y-%m-%d")

        current_capacity: int = sum(
            [
                reserve.numberOfRooms
                for reserve in self.reservations
                if reserve.has_date_conflict(in_date, out_date)
            ]
        )
        return not (current_capacity + number_of_rooms > self.max_capacity)

    def __key__(self):
        return self.hotel_id
