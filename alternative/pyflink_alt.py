from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.functions import (
    KeyedProcessFunction,
    RuntimeContext,
    ValueStateDescriptor,
    ValueState,
)
import json

# 25 lines
class UserOperator(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("state", Types.BYTE())
        self.state: ValueState = runtime_context.get_state(descriptor)

    def process_element(self, event, ctx: KeyedProcessFunction.Context):
        user = json.loads(self.state.value())
        username = event["username"]
        password = event["password"]

        if event["type"] == "CREATE_USER":
            user_item = {username: username, password: password}
            self.state.update(json.dumps(user_item))

            yield {"message": "created a user!"}
        elif event["type"] == "LOGIN_USER":
            if user is None:
                yield {"message": "user not found"}
            else:
                yield {"message": user["password"] == password}


env: StreamExecutionEnvironment = StreamExecutionEnvironment.get_execution_environment()
env.from_source(FlinkKafkaConsumer()).map(lambda x: json.loads(x)).key_by(
    lambda x: x["username"]
).process(UserOperator()).sink_to(FlinkKafkaProducer())

env.run()
