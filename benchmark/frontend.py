from .hotel.user import User
from .hotel.hotel import Hotel

import stateflow
from stateflow.client.fastapi.kafka import KafkaFastAPIClient

client = KafkaFastAPIClient(stateflow.init())
app = client.get_app()