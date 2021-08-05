from benchmark.hotel.reservation import Reservation
from stateflow import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref


def test_create_reservation():
    reservation = Reservation("1", 10)
    reservation.max_capacity = 10
    reservation.hotel_id = "1"


def test_reservations():
    reservation = Reservation("2", 1)
    reservation.max_capacity = 2

    assert reservation.check_availability("2021-01-01", "2021-01-01", 1) is True
    assert reservation.add_reservation("Wouter", "2021-01-01", "2021-01-01", 1) is True
    assert (
        reservation.add_reservation("Kyriakos", "2021-01-01", "2021-01-01", 1) is True
    )
    assert (
        reservation.add_reservation("Asterios", "2021-01-01", "2021-01-01", 1) is False
    )  # hotel is full
    assert reservation.add_reservation("Wouter", "2021-01-08", "2021-01-12", 2) is True
    assert reservation.add_reservation("Wouter", "2021-01-09", "2021-01-11", 1) is False
