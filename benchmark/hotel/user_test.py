from benchmark.hotel.user import User
from stateflow.util.stateflow_test import stateflow_test

def test_create_user():
    user = User("test-user", "password", 10)

    assert user.balance == 10
    assert user.password == "password"
    assert user.username == "test-user"

def test_password_user():
    user = User("test-user", "password", 10)

    assert user.login("password")
    assert not user.login("wrong")

def test_pay():
    user = User("test-user", "password", 10)

    assert user.pay(10)
    assert user.balance == 0
    assert user.pay(0)
    assert user.balance == 0
    assert not user.pay(1)

def test_refund():
    user = User("test-user", "password", 10)

    assert user.pay(10)
    assert user.balance == 0
    user.refund(11)
    assert user.balance == 11
    user.refund(5)
    assert user.balance == 16