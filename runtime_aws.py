print("I'm here!")
from benchmark.hotel.user import User
print("Imported User")
from benchmark.hotel.search import Search, Geo, Rate
print("Imported Search, Geo, Rate")
from benchmark.hotel.reservation import Reservation
print("Imported Reservation")
from benchmark.hotel.profile import Profile, HotelProfile
print("Imported Profile, HotelProfile")
from benchmark.hotel.recommend import RecommendType, Recommend, stateflow
print("Imported RecommendType, Recommend and stateflow")

from stateflow.runtime.aws.gateway_lambda import AWSGatewayLambdaRuntime
print("Imported AWSGatewayLambdaRuntime")
# Initialize stateflow
flow = stateflow.init()
print("INIT")

runtime, handler = AWSGatewayLambdaRuntime.get_handler(flow, gateway=False)
