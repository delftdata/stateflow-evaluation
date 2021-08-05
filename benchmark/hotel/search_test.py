from benchmark.hotel.search import Search, Geo, Rate
from stateflow import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref


def test_create_search():
    search = Search("search-0")
    assert search.search_id == "search-0"


def test_search_nearby():
    geo = Geo("geo-0", 80)
    rate = Rate("rate-0", 80)
    search = Search("search-0")
    assert len(search.nearby("37.7867", "-122.4112", geo, rate)) == 4
