from .hotel.user import User
from .hotel.hotel import Hotel

import stateflow
import asyncio
from stateflow.client.fastapi.kafka import KafkaFastAPIClient, StateflowFailure

client = KafkaFastAPIClient(stateflow.init())
app = client.get_app()

@app.get("/create_users")
async def create_all_users():
    created = 0
    not_created = 0
    for f in asyncio.as_completed([User(f"wouter-{i}", "random", 100) for i in range(500)]):
        try:
            user = await f
            if isinstance(user, StateflowFailure):
                not_created += 1
                print(user.error_msg)
            else:
                created += 1
        except StateflowFailure as exc:
            print(exc.error_msg)
            not_created += 1

    return {"created": created, "not_created": not_created, "total": created + not_created}