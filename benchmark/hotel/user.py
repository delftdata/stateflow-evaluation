import stateflow


@stateflow.stateflow
class User:
    def __init__(self, username: str, password: str, balance: int):
        self.username: str = username
        self.password: str = password
        self.balance: int = balance

    def pay(self, amount: int) -> bool:
        if self.balance - amount < 0:
            return False

        self.balance -= amount
        return True

    def refund(self, amount: int):
        self.balance += amount

    def login(self, password: str) -> bool:
        return self.password == password

    def __key__(self):
        return self.username
