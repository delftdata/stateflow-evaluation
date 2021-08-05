from benchmark.hotel.frontend import Frontend, Geo, Profile, Search, Rate
from stateflow import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref

def test_frontend_create():
    frontend = Frontend("1")
    assert frontend.__key__() == "frontend_1"

def test_simple_search():
    frontend = Frontend("1")
    geo = Geo("geo_1", 80)
    profile = Profile("profile_1", 80)
    search = Search("search_1")
    rate = Rate("rate_1", 80)

    profiles = profile.get_profiles(geo.nearby("37.7867", "-122.4112"))
    print(visualize_ref(frontend, "search"))
    assert frontend.search("2021-01-01", "2021-01-01", "37.7867", "-122.4112") == profiles