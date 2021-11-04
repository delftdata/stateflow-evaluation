from statefun import *
import json

functions = StatefulFunctions()
@functions.bind(typename='nl.tudelft.benchmark/user', specs=[ValueSpec(name='user', type=StringType)])
async def greet(ctx: Context, message: Message):
    user_state = ctx.storage.user

    event = json.loads(message.event)
    username = event["username"]
    password = event["password"]

    reply = None

    if event["type"] == "CREATE_USER":
        user_item = {username: username, password: password}
        context.storage.user = json.dumps(user_item)

        reply = {"message": "created a user!"}
    elif event["type"] == "LOGIN_USER":
        if user_state is None:
            reply = {"message": "user not found"}
        else:
            user = json.loads(user_state)
            if user["password"] == password:
                reply = {"message": False}
            else:
                reply = {"message": True}

    context.send_egress(kafka_egress_message(typename='nl.delft.benchmark/reply',
                                             topic='reply',
                                             key=username,
                                             value=reply))
