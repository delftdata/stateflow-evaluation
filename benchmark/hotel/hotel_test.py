from benchmark.hotel.hotel import Hotel, Room, User, Reservation
from stateflow import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref
import datetime


def test_create_hotel():
    room = Room(0, 10, 100, [])
    hotel = Hotel("0", [room])

    assert hotel.hotel_id == "0"
    assert hotel.rooms == room


def test_reserve_incorrect_password():
    user = User("wouter", "123", 10000)
    room = Room(0, 10, 100, [])
    hotel = Hotel("0", [room])

    check_in_date = datetime.datetime(year=2021, month=1, day=1)
    check_out_date = datetime.datetime(year=2021, month=1, day=5)
    result, output = hotel.reserve(user, "12345", check_in_date, check_out_date, 10)

    print(output)
    assert not result
    assert output == "Incorrect password!"


def test_reserve_hotel_simple():
    user = User("wouter", "123", 10000)
    room = Room(0, 10, 100, [])
    hotel = Hotel("0", [room])

    check_in_date = datetime.datetime(year=2021, month=1, day=1)
    check_out_date = datetime.datetime(year=2021, month=1, day=5)
    result, output = hotel.reserve(user, "123", check_in_date, check_out_date, 10)

    print(output)
    assert result
    assert len(hotel.rooms.reservations) == 1
    assert user.balance == 10000 - 400

    # Try it again this time it will fail, because the room is full.
    result, output = hotel.reserve(user, "123", check_in_date, check_out_date, 10)
    print(output)

    assert not result
    assert len(hotel.rooms.reservations) == 1
    assert user.balance == 10000 - 400
