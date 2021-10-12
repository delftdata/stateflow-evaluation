from benchmark.hotel.user import User
from benchmark.hotel.search import Search, Geo, Rate
from benchmark.hotel.reservation import Reservation
from benchmark.hotel.profile import Profile, HotelProfile
from benchmark.hotel.recommend import RecommendType, Recommend, stateflow

from stateflow.runtime.dataflow.remote_lambda import RemoteLambda

# Initialize stateflow
flow = stateflow.init()

runtime, handler = RemoteLambda.get_handler(flow)
