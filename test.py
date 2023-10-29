from FlightIncrease.GetInterval import GetInterval
from FlightIncrease.GetWingSpan import GetWingSpan
from FlightIncrease.IncreaseFlight import _is_overlapping, _conflict_half, _conflict_all
from FlightIncrease.IntervalType import IntervalBase

HOUR = 60 * 60


def test_get_data():
    instance = GetInterval(filename="data/mock.csv")
    for i in range(len(instance.data["callsign"])):
        if instance.data["callsign"][i][-2:] == "ar":
            assert instance.data["arrivee"][i] == "ZBTJ"
        else:
            assert instance.data["departure"][i] == "ZBTJ"


def test_get_interval_one():
    instance = GetInterval(filename="data/mock.csv")
    for r in instance.data["registration"]:
        inst_list = instance._get_interval_one(r)
        for i in inst_list:
            assert i.interval >= 0


def test_flight_list_sorted():
    instance = GetInterval(filename="data/mock.csv")
    flight_list = instance.flight_list_sorted("B9987")
    for i in range(len(flight_list) - 1):
        if instance.data["departure"][flight_list[i]] == "ZBTJ":
            assert (
                instance.data["ATOT"][flight_list[i]]
                <= instance.data["ALDT"][flight_list[i + 1]]
            )
        else:
            assert (
                instance.data["ALDT"][flight_list[i]]
                <= instance.data["ATOT"][flight_list[i + 1]]
            )


def test_get_interval():
    instance = GetInterval(filename="data/mock.csv")
    inst_list = instance.get_interval()
    assert len(inst_list) == 35
    for i in inst_list:
        assert i.begin_interval < i.end_interval
        assert i.interval >= 900
    assert inst_list[25].end_interval - inst_list[25].begin_interval == 3060


def test_get_gate_size():
    increase_inst = GetWingSpan()
    gate_size = increase_inst.gatesize
    for g in gate_size["size_limit"]:
        assert g >= 24.9
        assert g <= 80


def test_conflict_half():
    inst_1 = IntervalBase(
        [900, 1800, 2700, "CA", "B9985", "B9985 de", "B9985 ar", 24.9, "414"]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "CA", "B9986", "B9986 de", "B9986 ar", 24.9, "414R"]
    )
    inst_3 = IntervalBase(
        [900, 1200, 2100, "CA", "B9987", "B9987 de", "B9987 ar", 24.9, "414L"]
    )
    inst_4 = IntervalBase(
        [900, 0, 900, "CA", "B9988", "B9988 de", "B9988 ar", 24.9, "414L"]
    )
    inst_5 = IntervalBase(
        [900, 1200, 2100, "CA", "B9989", "B9989 de", "B9989 ar", 24.9, "415"]
    )

    # Test Case 1: Overlapping intervals with dependent gate (414 414L/414R)
    assert _conflict_half(inst_1, inst_2, "414L", False) == False
    assert _conflict_half(inst_1, inst_2, "414R", False) == True
    assert _conflict_half(inst_1, inst_3, "414L", False) == True

    # Test Case 2: Overlapping intervals with dependent gate (414L 414R)
    assert _conflict_half(inst_2, inst_3, "414R", False) == False

    # Test Case 3: Non-overlapping intervals with dependent gate (414L 414L)
    assert _conflict_half(inst_3, inst_4, "414L", False) == False

    # Test Case 4: Overlapping intervals but different gate
    assert _conflict_half(inst_2, inst_5, "414L", False) == False


def test_conflict_all():
    inst_1 = IntervalBase(
        [900, 1800, 2700, "CA", "B9985", "B9985 de", "B9985 ar", 24.9, "414"]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "CA", "B9986", "B9986 de", "B9986 ar", 24.9, "414R"]
    )
    inst_3 = IntervalBase(
        [900, 1200, 2100, "CA", "B9987", "B9987 de", "B9987 ar", 24.9, "414L"]
    )
    inst_4 = IntervalBase(
        [900, 0, 900, "CA", "B9988", "B9988 de", "B9988 ar", 24.9, "414"]
    )
    inst_5 = IntervalBase(
        [900, 1200, 2100, "CA", "B9989", "B9989 de", "B9989 ar", 24.9, "415"]
    )

    # Test Case 1: Overlapping intervals with dependent gate (414 414L/414R)
    assert _conflict_all(inst_1, inst_2, "414", False) == True
    assert _conflict_all(inst_1, inst_3, "414", False) == True

    # Test Case 2: Non-overlapping intervals with dependent gate (414L 414L)
    assert _conflict_all(inst_1, inst_4, "414", False) == False

    # Test Case 4: Overlapping intervals but different gate
    assert _conflict_all(inst_1, inst_5, "414", False) == False


def test_is_overlapping():
    # 时间段1和时间段2重叠
    assert _is_overlapping((1, 5), (3, 7)) == True

    # 时间段1在时间段2之前
    assert _is_overlapping((1, 5), (7, 10)) == False

    # 时间段1在时间段2之后
    assert _is_overlapping((10, 15), (1, 5)) == False

    # 时间段1和时间段2完全相同
    assert _is_overlapping((5, 10), (5, 10)) == True

    # 时间段1的结束时间等于时间段2的开始时间
    assert _is_overlapping((1, 5), (5, 10)) == True

    # 时间段1的开始时间等于时间段2的结束时间
    assert _is_overlapping((5, 10), (1, 5)) == True

    # 一个时间段包含另一个时间段
    assert _is_overlapping((1, 10), (3, 7)) == True
