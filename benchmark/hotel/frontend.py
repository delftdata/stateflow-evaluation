import stateflow


@stateflow.stateflow
class Frontend:
    def __init__(self, client_id: str):
        self.client_id = client_id

    # We store a list of coords here, for the nearby handler.

    def init(self):
        return

    def search_hotels(self):
        pass
