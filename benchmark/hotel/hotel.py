from typing import List, Tuple, Optional
from dataclasses import dataclass, field
import datetime
from benchmark.hotel.user import User
import stateflow


@dataclass
class Reservation:

    customer_name: str
    check_in_date: datetime
    check_out_date: datetime

    def has_date_conflict(self, in_date: datetime, out_date: datetime) -> bool:
        """ Checks if the reservation overlaps with another (potential) reservation.
        Based on https://stackoverflow.com/a/325964

        :param in_date: the start of the potential reservation.
        :param out_date: the end of the potential reservation.
        :return: whether they conflict.
        """
        return in_date <= self.check_out_date and out_date >= self.check_in_date


@dataclass
class Room:

    room_number: int
    capacity: int
    rate: int
    reservations: List[Reservation] = field(default_factory=[])

    def is_available(self, in_date: datetime, out_date: datetime) -> bool:
        """ Checks if a room is available for a certain time range.

        :param in_date: the check in date.
        :param out_date: the check out date.
        :return: whether or not a room is available.
        """
        for reservation in self.reservations:
            if reservation.has_date_conflict(in_date, out_date):
                return False

        return True

    def make_reservation(
        self, customer_name: str, in_date: datetime, out_date: datetime
    ) -> bool:
        """ Make a reservation.

        Once again, check if the room is actually available. We need to do this check to ensure consistency.

        :param customer_name: the name of the customer.
        :param in_date: the check in date.
        :param out_date: the check out date.
        :return: if the reservation is successful.
        """
        if not self.is_available(in_date, out_date):
            return False

        self.reservations.append(Reservation(customer_name, in_date, out_date))
        return True


@stateflow.stateflow
class Hotel:
    def __init__(self, hotel_id: str, rooms: List[Room]):
        self.hotel_id: str = hotel_id
        self.rooms: List[Room] = rooms

    def reserve(
        self,
        user: User,
        password: str,
        check_in_date: datetime,
        check_out_date: datetime,
        amount_of_guests: int,
    ) -> Tuple[bool, str]:
        """ Reserves a hotel room.

        :param user: the user/customer for which to reserve.
        :param password: the password of the user.
        :param check_in_date: the preferred check in date.
        :param check_out_date: the preferred check out date.
        :param amount_of_guests: the preferred amount of guests.
        :return: either a successful reservation or not.
        """

        # Login the user.
        if not user.login(password):
            return False, "Incorrect password!"

        # Get the name of the customer.
        customer_name: str = user.username

        # Find the first room by dates and capacity.
        room: Optional[Room] = self.get_room_by_availability(
            check_in_date, check_out_date, amount_of_guests
        )

        # If no room can be found, there is no reservation to make.
        if not room:
            return False, "No rooms available for this time range or amount of guests."

        # Compute the total price.
        total_price: int = room.rate * (check_out_date - check_in_date).days

        # Room is available, let the user pay.
        if not user.pay(total_price):
            return (
                False,
                "Room available, but user did not have a sufficient balance to pay the room.",
            )

        # If the actual reservation fails, refund the payment to the user (SAGA style).
        if not room.make_reservation(customer_name, check_in_date, check_out_date):
            user.refund(total_price)
            return False, "No rooms available for this time range or amount of guests."

        return (
            True,
            f"Successful reservation for room {room.room_number} "
            f"from {check_in_date.strftime('%d-%m-%y')} to {check_out_date.strftime('%d-%m-%y')} "
            f"with a total cost of {total_price}EU.",
        )

    def get_room_by_availability(
        self, in_date: datetime, out_date: datetime, amount_of_guests: int
    ) -> Optional[Room]:
        """ Finds the first available room by check-in and out date + the desired room size.

        It does not consider preferences with regard to the price of the room and returns the first one available.

        :param in_date: the check in date.
        :param out_date: the check out date.
        :param amount_of_guests: the amount of guests (i.e. minimal room size).
        :return: a room if one is available.
        """
        for room in self.rooms:
            if room.capacity >= amount_of_guests and room.is_available(
                in_date, out_date
            ):
                break
        else:
            return None

        return room

    def __key__(self) -> str:
        return self.hotel_id
