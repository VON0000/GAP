from FlightIncrease.GetInterval import GetInterval
from FlightIncrease.GetWingSpan import GetWingSpan
from FlightIncrease.IncreaseFlight import _is_overlapping

HOUR = 60 * 60


def test_get_data():
    instance = GetInterval(filename="./data/test.csv")
    for i in range(len(instance.data["callsign"])):
        if instance.data["callsign"][i][-2:] == "ar":
            assert instance.data["arrivee"][i] == "ZBTJ"
        else:
            assert instance.data["departure"][i] == "ZBTJ"


def test_get_interval_one():
    instance = GetInterval(filename="./data/test.csv")
    for r in instance.data["registration"]:
        inst_list = instance._get_interval_one(r)
        for i in inst_list:
            assert i.interval >= 0


def test_flight_list_sorted():
    instance = GetInterval(filename="./data/test.csv")
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
    instance = GetInterval(filename="./data/test.csv")
    inst_list = instance.get_interval()
    assert len(inst_list) == 35
    for i in inst_list:
        assert i.begin_interval < i.end_interval
        assert i.interval >= 900


def test_get_gate_size():
    increase_inst = GetWingSpan()
    gate_size = increase_inst.gatesize
    for g in gate_size["size_limit"]:
        assert g >= 24.9
        assert g <= 80


def test_find_size():
    ...


def test_find_conflict():
    ...


def test_find_suitable_gate():
    ...


def test_increase_flight():
    ...


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
