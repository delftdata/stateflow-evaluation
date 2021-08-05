from benchmark.hotel.profile import Profile
from stateflow import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref


def test_create_profile():
    profile = Profile("profile-0", 80)
    assert profile.profile_id == "profile-0"
    assert len(profile.profiles) == 80


def test_get_profiles():
    profile = Profile("profile-0", 80)

    assert len(profile.get_profiles(["9", "13", "26"])) == 3
    assert [prof.id for prof in profile.get_profiles(["9", "13", "26"])] == [
        "9",
        "13",
        "26",
    ]

    assert [
        prof.id for prof in profile.get_profiles([str(x) for x in range(1, 81)])
    ] == [str(x) for x in range(1, 81)]
