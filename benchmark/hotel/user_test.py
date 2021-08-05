from benchmark.hotel.user import User
from stateflow.util.stateflow_test import stateflow_test


def test_create_user():
    user = User("test-user", "password")

    assert user.password == "password"
    assert user.username == "test-user"


def test_password_user():
    user = User("test-user", "password")

    assert user.login("password")
    assert not user.login("wrong")
