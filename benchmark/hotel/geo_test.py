from benchmark.hotel.geo import Geo
from stateflow import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref

def test_create_geo():
    geo = Geo("geo-0")
    assert geo.geo_id == "geo-0"
    assert len(geo.geo_points) == 80

def test_get_nearby():
    geo = Geo("geo-1")
    print(visualize_ref(geo, "nearby"))
    
    assert len(geo.nearby("37.7867", "-122.4112")) == 5
    assert geo.nearby("37.7867", "-122.4112")[0] == "1"


