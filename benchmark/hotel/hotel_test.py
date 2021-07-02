from benchmark.hotel.hotel import Hotel, Room, User
from stateflow import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref
import datetime

def test_create_hotel():
    room = Room(0, 10, 100, [])
    hotel = Hotel("0", [room])

    assert hotel.hotel_id == "0"
    assert hotel.rooms == room

def test_reserve_hotel(stateflow_test):
    user = User("wouter", "123", 100)
    room = Room(0, 10, 100, [])
    hotel = Hotel("0", [room])

    check_in_date = datetime.datetime(year=2021, month=1, day=1)
    check_out_date = datetime.datetime(year=2021, month=1, day=5)


    result, output = hotel.reserve(user, "123", check_in_date, check_out_date, 1)
    print(output)
    assert result