import uuid

from user import User
from search import Search, Geo, Rate
from reservation import Reservation
from hprofile import Profile, HotelProfile
from recommend import RecommendType, Recommend, stateflow

from stateflow.runtime.flink.pyflink import FlinkRuntime
from stateflow.serialization.pickle_serializer import PickleSerializer

# Initialize stateflow
flow = stateflow.init()

BUNDLE_TIME = 5
BUNDLE_SIZE = 1000

consumer_config = {
    "bootstrap.servers": "",
     "group.id": str(uuid.uuid4()),
    "auto.offset.reset": "latest",
}
producer_config = {
    "bootstrap.servers": "",

}
runtime = FlinkRuntime(
    flow,
    serializer=PickleSerializer(),
    bundle_size=BUNDLE_SIZE,
    bundle_time=BUNDLE_TIME,
    producer_config=producer_config,
    consumer_config=consumer_config,
)
runtime.run()
