from hotel.user import User
from stateflow.runtime.flink_runtime import FlinkRuntime
from stateflow.runtime.beam_runtime import BeamRuntime
import stateflow
from stateflow.serialization.pickle_serializer import PickleSerializer

# Initialize stateflow
flow = stateflow.init()

runtime = BeamRuntime(flow, serializer=PickleSerializer())
runtime.run()
