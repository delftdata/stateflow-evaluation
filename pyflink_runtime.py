from benchmark.hotel.user import User
from benchmark.hotel.search import Search, Geo, Rate
from benchmark.hotel.reservation import Reservation
from benchmark.hotel.profile import Profile, HotelProfile
from benchmark.hotel.recommend import RecommendType, Recommend, stateflow

from stateflow.runtime.flink.pyflink import FlinkRuntime
from stateflow.serialization.pickle_serializer import PickleSerializer

# Initialize stateflow
flow = stateflow.init()

runtime = FlinkRuntime(flow, serializer=PickleSerializer())
runtime.run()
