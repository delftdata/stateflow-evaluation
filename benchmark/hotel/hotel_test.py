from benchmark.hotel.hotel import Hotel, Room
from stateflow.util.stateflow_test import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref


def test_create_hotel():
    room = Room(0, 10, 100, [])
    hotel = Hotel("0", [room])

    print(visualize_ref(hotel, "reserve"))

    assert hotel.hotel_id == "0"
    assert hotel.rooms == room
