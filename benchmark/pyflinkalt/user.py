import stateflow


@stateflow.stateflow
class User:
    def __init__(self, username: str, password: str):
        self.username: str = username
        self.password: str = password

    def login(self, password: str) -> bool:
        return self.password == password

    def __key__(self):
        return self.username
