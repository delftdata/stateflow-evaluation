from benchmark.hotel.recommend import Recommend, RecommendType
from stateflow import stateflow_test
from stateflow.util.dataflow_visualizer import visualize_ref


def test_create_recommend():
    recommend = Recommend("recommend-0", 80)
    assert recommend.recommend_id == "recommend-0"
    assert len(recommend.hotels) == 80


def test_recommend():
    recommend = Recommend("recommend-1", 80)

    assert list(
        recommend.recommend(RecommendType.DISTANCE, {"lat": 37.7867, "lon": -122.4112})
    ) == ["1"]
    assert list(recommend.recommend(RecommendType.RATE, {})) == [
        "9",
        "24",
        "39",
        "54",
        "69",
    ]
    assert list(recommend.recommend(RecommendType.PRICE, {})) == ["2"]
