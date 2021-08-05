from benchmark.hotel.rate import Rate
from stateflow import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref


def test_create_rate():
    rate = Rate("rate-0", 80)
    assert rate.rate_id == "rate-0"
    assert len(rate.rate_plans) == 28


def test_get_rates():
    rate = Rate("rate-1", 80)
    assert rate.rate_id == "rate-1"
    print(rate.get_rates())
    assert len(rate.get_rates()) == 28
