from FlightIncrease.GetInterval import GetInterval, IncreaseFlight

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
    interval_inst = GetInterval(filename="./data/test.csv")
    increase_inst = IncreaseFlight(interval_inst.interval)
    gate_size = increase_inst.get_gate_size()
    for g in gate_size["size_limit"]:
        assert g >= 24.9
        assert g <= 80
