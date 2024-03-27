import math

from BasicFunction.GetInterval import GetInterval
from refactorGateAllocation.GetTaxiingTime import GetTaxiingTime


def test_get_taxiing_time():
    data = GetTaxiingTime("101", "MANEX").get_taxiing_time()

    # 414L 290 525 335 290 510 340 290 520 335 290 510 340
    assert data["414L"] == {
        "MANEX": {
            "DEP-16R": 290,
            "ARR-16L": 525,
            "ARR-16R": 335
        },
        "MIN": {
            "DEP-16R": 290,
            "ARR-16L": 510,
            "ARR-16R": 340
        },
        "PN_MANEX": {
            "DEP-16R": 290,
            "ARR-16L": 520,
            "ARR-16R": 335
        },
        "PN_MIN": {
            "DEP-16R": 290,
            "ARR-16L": 510,
            "ARR-16R": 340
        }
    }

    # 117 490 390 280 490 380 260 490 390 280 490 365 260
    assert data["117"] == {
        "MANEX": {
            "DEP-16R": 490,
            "ARR-16L": 390,
            "ARR-16R": 280
        },
        "MIN": {
            "DEP-16R": 490,
            "ARR-16L": 380,
            "ARR-16R": 260
        },
        "PN_MANEX": {
            "DEP-16R": 490,
            "ARR-16L": 390,
            "ARR-16R": 280
        },
        "PN_MIN": {
            "DEP-16R": 490,
            "ARR-16L": 365,
            "ARR-16R": 260
        }
    }


def test_transform_second_to_half_minute():
    interval_half_minute = GetInterval(filename="../data\\mock_231029.csv", quarter=math.nan)
    interval_half_minute.transform_second_to_half_minute()

    interval_second = GetInterval(filename="../data\\mock_231029.csv", quarter=math.nan)

    for i in range(len(interval_half_minute.interval)):
        assert interval_half_minute.interval[i].begin_interval == math.ceil(
            interval_second.interval[i].begin_interval / 30)

        assert interval_half_minute.interval[i].end_interval == math.ceil(
            interval_second.interval[i].end_interval / 30)

        assert interval_half_minute.interval[i].interval == math.ceil(
            interval_second.interval[i].interval / 30)
