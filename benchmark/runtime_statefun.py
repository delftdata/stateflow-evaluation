from benchmark.hotel.user import User
from benchmark.hotel.search import Search, Geo, Rate
from benchmark.hotel.reservation import Reservation
from benchmark.hotel.profile import Profile, HotelProfile
from benchmark.hotel.recommend import RecommendType, Recommend, stateflow

from stateflow.runtime.flink.statefun import StatefunRuntime, web
from stateflow.serialization.pickle_serializer import PickleSerializer
from stateflow.util.statefun_module_generator import generate

# Initialize stateflow
flow = stateflow.init()

print(generate(flow))

runtime = StatefunRuntime(flow, serializer=PickleSerializer())
app = runtime.get_app()


if __name__ == "__main__":
    web.run_app(app, port=8000)
