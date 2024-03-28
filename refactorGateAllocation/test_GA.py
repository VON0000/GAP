import math

from BasicFunction.GetData import get_data
from BasicFunction.GetInterval import GetInterval
from refactorGateAllocation.GetTaxiingPattern import TaxiingStatus
from refactorGateAllocation.GetTaxiingTime import get_all_taxiing_time, GetTaxiingTime


def test_get_all_taxiing_time():
    data = get_all_taxiing_time()

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


def test_get_taxiing_time():
    assert GetTaxiingTime("414L", "PN_MANEX").taxiing_time == {
        "DEP-16R": 290,
        "ARR-16L": 520,
        "ARR-16R": 335
    }
    assert GetTaxiingTime("117", "PN_MIN").taxiing_time == {
        "DEP-16R": 490,
        "ARR-16L": 365,
        "ARR-16R": 260
    }


def test_transform_second_to_half_minute():
    data = get_data("../data/mock_231029.csv")
    interval_half_minute = GetInterval(data, math.nan, 28)
    interval_half_minute.transform_second_to_half_minute()

    interval_second = GetInterval(data, math.nan, 28)

    for i in range(len(interval_half_minute.interval)):
        assert interval_half_minute.interval[i].begin_interval == math.ceil(
            interval_second.interval[i].begin_interval / 30)

        assert interval_half_minute.interval[i].end_interval == math.ceil(
            interval_second.interval[i].end_interval / 30)

        assert interval_half_minute.interval[i].interval == math.ceil(
            interval_second.interval[i].interval / 30)


def test_get_time_used():
    time_list = TaxiingStatus(data=get_data("../data/mock_231029.csv"), quarter=12, seuil=28)._get_time_used()
    assert 12840 in time_list
    assert 9420 in time_list

    assert 35880 not in time_list
    assert 41520 not in time_list

    time_list = TaxiingStatus(data=get_data("../data/mock_231029.csv"), quarter=50, seuil=28)._get_time_used()
    assert 35880 in time_list
    assert 41520 in time_list


def test_get_interval():
    data = get_data("../data/mock_231029.csv")
    instance = GetInterval(data, quarter=math.nan, seuil=3)
    inst_list = instance.get_interval(quarter=math.nan)
    for i in inst_list:
        if i.end_callsign == i.begin_callsign:
            inst_type = i.end_callsign[-2:]
            if inst_type == "de":
                assert i.end_qfu == i.begin_qfu
                assert i.begin_qfu == "DEP-16R"
        if i.begin_callsign == "CXA8229 ar":
            print("\nreach")
            assert i.begin_qfu == "ARR-16L"
        if i.begin_callsign == "CSC8861 ar":
            print("reach\n")
            assert i.begin_qfu == "ARR-16R"
