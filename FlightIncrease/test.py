from copy import deepcopy

import loguru
import numpy as np

from FlightIncrease import OutPut
from FlightIncrease.AircraftModel import AircraftModel
from FlightIncrease.AirlineType import get_airline_info, AirlineType, get_group_dict
from FlightIncrease.DelayTime import get_wake_turbulence, find_insertion_location
from FlightIncrease.GetInterval import GetInterval
from FlightIncrease.GetWingSpan import GetWingSpan
from FlightIncrease.IncreaseFlight import (
    _is_overlapping,
    _conflict_half,
    _conflict_all,
    IncreaseFlight,
)
from FlightIncrease.IntervalType import IntervalBase

HOUR = 60 * 60
TIME_DICT = {"ar": {"TTOT": 0, "TLDT": 0, "ATOT": 0, "ALDT": 0},
             "de": {"TTOT": 0, "TLDT": 0, "ATOT": 0, "ALDT": 0}}


def test_get_data():
    instance = GetInterval(filename="../data/mock_231029.csv")
    for i in range(len(instance.data["callsign"])):
        if instance.data["callsign"][i][-2:] == "ar":
            assert instance.data["arrivee"][i] == "ZBTJ"
        else:
            assert instance.data["departure"][i] == "ZBTJ"


def test_get_interval_one():
    instance = GetInterval(filename="../data/mock_231029.csv")
    for r in instance.data["registration"]:
        inst_list = instance._get_interval_one(r)
        for i in inst_list:
            assert i.interval >= 0


def test_flight_list_sorted():
    instance = GetInterval(filename="../data/mock_231029.csv")
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
    instance = GetInterval(filename="../data/mock_231029.csv")
    inst_list = instance.get_interval()
    assert len(inst_list) == 35
    for i in inst_list:
        if i.end_callsign == "HXA2844 de":
            continue
        # test: Verify when turning data time to interval time, the end_interval is equal to ATOT
        if i.end_callsign[-2:] == "de":
            index = set(
                np.where(np.array(instance.data["callsign"]) == i.end_callsign)[0]
            ) & set(np.where(np.array(instance.data["departure"]) == "ZBTJ")[0])
            assert i.end_interval == instance.data["ATOT"][list(index)[0]]
        # test: Verify when turning data time to interval time, the begin_interval is equal to ALDT + 5 * 60
        if i.begin_callsign[-2:] == "ar":
            index = set(
                np.where(np.array(instance.data["callsign"]) == i.begin_callsign)[0]
            ) & set(np.where(np.array(instance.data["arrivee"]) == "ZBTJ")[0])
            assert i.begin_interval == instance.data["ALDT"][list(index)[0]] + 5 * 60
    assert inst_list[25].end_interval - inst_list[25].begin_interval == 3060


def test_get_gate_size():
    increase_inst = GetWingSpan()
    gate_size = increase_inst.gatesize
    for g in gate_size["size_limit"]:
        assert g >= 24.9
        assert g <= 80


def test_conflict_half():
    inst_1 = IntervalBase(
        [900, 1800, 2700, "CA", "B9985", "B9985 de", "B9985 ar", 24.9, "414", "B737", TIME_DICT]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "CA", "B9986", "B9986 de", "B9986 ar", 24.9, "414R", "B737", TIME_DICT]
    )
    inst_3 = IntervalBase(
        [900, 1200, 2100, "CA", "B9987", "B9987 de", "B9987 ar", 24.9, "414L", "B737", TIME_DICT]
    )
    inst_4 = IntervalBase(
        [900, 0, 900, "CA", "B9988", "B9988 de", "B9988 ar", 24.9, "414L", "B737", TIME_DICT]
    )
    inst_5 = IntervalBase(
        [900, 1200, 2100, "CA", "B9989", "B9989 de", "B9989 ar", 24.9, "415", "B737", TIME_DICT]
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
        [900, 1800, 2700, "CA", "B9985", "B9985 de", "B9985 ar", 24.9, "414", "B737", TIME_DICT]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "CA", "B9986", "B9986 de", "B9986 ar", 24.9, "414R", "B737", TIME_DICT]
    )
    inst_3 = IntervalBase(
        [900, 1200, 2100, "CA", "B9987", "B9987 de", "B9987 ar", 24.9, "414L", "B737", TIME_DICT]
    )
    inst_4 = IntervalBase(
        [900, 0, 900, "CA", "B9988", "B9988 de", "B9988 ar", 24.9, "414", "B737", TIME_DICT]
    )
    inst_5 = IntervalBase(
        [900, 1200, 2100, "CA", "B9989", "B9989 de", "B9989 ar", 24.9, "415", "B737", TIME_DICT]
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


def test_get_airline_info():
    airline_info = get_airline_info("cargo")
    assert list(airline_info.keys()) == [
        "AirBridgeCargoAirlines",
        "AVIC",
        "AisaMedical",
        "ChinaCargoAirlines",
        "ChinaPost",
        "DeerJet",
        "GOMEHoldings",
        "LonghaoAirlines",
        "MinshengFinancialLeasing",
        "MLLIN",
        "private",
        "SHUNFENG",
        "Taixiang",
        "TianjinAirCargo",
        "VistaJet",
        "YalianBusinessJet",
        "YangtzeRiverExpress",
    ]
    airline_info = get_airline_info("domestic")
    assert list(airline_info.keys()) == [
        "Joyair",
        "AIRCRANE",
        "BeijingAirlines",
        "ChengduAirlines",
        "COLORFUL",
        "GuizhouAirlines",
        "HEBEIAIRLINES",
        "LIANHANG",
        "LoongAir",
        "SENDI",
        "ShanghaiJuneyaoAirlines",
        "ShanghaiSpringAirlines",
        "SichuanAirlines",
        "SKYLEGEND",
        "SPRAY",
        "SRJET",
        "TIBET",
        "TRANSJADE",
        "XIANGJIAN",
        "ZhejiangLoongAlrlines",
        "Chinaexpressair",
        "Westair",
        "TianjinAirlines",
        "STRAITAIR",
        "LUCKYAIR",
        "HainanAirlines",
        "DONGHAIAIR",
        "BeijingCapitalAirlines",
        "XiamenAirlines",
        "OkayAirways",
        "ShanghaiAirlines",
        "ChinaSouthernAirlines",
        "ChinaEasternAirlines",
        "ShenzhenAirlines",
        "shandongAirlines",
        "AirChina",
    ]
    airline_info = get_airline_info("international")
    assert list(airline_info.keys()) == [
        "AirAsiaX",
        "AirChinaInternationalCorporation",
        "AirMacau",
        "AllNipponAirways",
        "AsianaAirways",
        "EmpireAviation",
        "EVAAir",
        "HongKongAirlines",
        "JapanAirlines",
        "KoreanAirLines",
        "MalindoAir",
        "NewEraofThaiAirways",
        "NokScoot",
        "PTLionMentariAirlines",
        "SCOOTER",
        "Sky Angkor Airlines",
        "SouthAfricanAirways",
        "SpringJapan",
        "ThaiLionAir",
        "TurkishAirlines",
        "VientnamAirlines",
        "VietJet",
        "TransMediterraneanAirways",
        "FarEastern",
    ]


def test_get_type():
    airline = AirlineType("AirChina")
    assert airline.type == "domestic"

    airline = AirlineType("YangtzeRiverExpress")
    assert airline.type == "cargo"

    airline = AirlineType("AirAsiaX")
    assert airline.type == "international"


def test_get_available_gate():
    airline = AirlineType("AirChina")
    assert airline.available_gate == [
        "107",
        "108",
        "109",
        "117",
        "118",
        "201",
        "202",
        "203",
    ]

    airline = AirlineType("YangtzeRiverExpress")
    assert airline.available_gate == [
        "874",
        "875",
        "876",
        "877",
        "878",
        "879",
        "884",
        "885",
        "886",
        "887",
        "888",
        "889",
        "890",
        "891",
        "892",
        "893",
        "894",
        "895",
        "896",
        "897",
        "898",
        "899",
        "901",
        "902",
        "903",
        "904",
        "905",
        "906",
        "907",
        "908",
        "909",
        "910",
        "911",
        "912",
        "913",
        "914",
        "915",
        "916",
        "921",
        "922",
        "923",
        "924",
        "925",
        "886L",
        "886R",
        "887L",
        "887R",
        "898L",
        "898R",
        "899L",
        "899R",
        "910R",
        "911R",
        "912R",
    ]

    airline = AirlineType("AirAsiaX")
    assert airline.available_gate == ["101", "102", "103", "104", "105", "106"]


def test_get_group_dict():
    group_dict = get_group_dict()
    assert set(group_dict["cargo"]) == {
        "874",
        "875",
        "876",
        "877",
        "878",
        "879",
        "884",
        "885",
        "886",
        "887",
        "888",
        "889",
        "890",
        "891",
        "892",
        "893",
        "894",
        "895",
        "896",
        "897",
        "898",
        "899",
        "901",
        "902",
        "903",
        "904",
        "905",
        "906",
        "907",
        "908",
        "909",
        "910",
        "911",
        "912",
        "913",
        "914",
        "915",
        "916",
        "921",
        "922",
        "923",
        "924",
        "925",
        "886L",
        "886R",
        "887L",
        "887R",
        "898L",
        "898R",
        "899L",
        "899R",
        "910R",
        "911R",
        "912R",
    }
    assert set(group_dict["international"]) == {
        "101",
        "102",
        "103",
        "104",
        "105",
        "106",
    }
    assert set(group_dict["domestic"]) == {
        "107",
        "108",
        "109",
        "110",
        "111",
        "112",
        "113",
        "114",
        "115",
        "116",
        "117",
        "118",
        "201",
        "202",
        "203",
        "204",
        "205",
        "206",
        "207",
        "208",
        "209",
        "210",
        "211",
        "212",
        "213",
        "214",
        "215",
        "216",
        "217",
        "218",
        "219",
        "220",
        "221",
        "222",
        "223",
        "224",
        "225",
        "226",
        "227",
        "228",
        "229",
        "230",
        "409",
        "410",
        "411",
        "412",
        "413",
        "414",
        "415",
        "416",
        "417",
        "418",
        "419",
        "501",
        "502",
        "503",
        "504",
        "601",
        "602",
        "603",
        "604",
        "605",
        "606",
        "607",
        "608",
        "609",
        "610",
        "414L",
        "414R",
        "415L",
        "415R",
        "416L",
        "416R",
        "417L",
        "417R",
        "418L",
        "418R",
        "419L",
        "419R",
    }


@loguru.logger.catch()
def test_get_index_range():
    inst_1 = IntervalBase(
        [900, 1800, 2700, "CA0", "B9985", "B9985 de", "B9985 ar", 24.9, "414", "B737", TIME_DICT]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "CA1", "B9987", "B9986 de", "B9986 ar", 24.9, "414R", "B737", TIME_DICT]
    )
    inst_3 = IntervalBase(
        [900, 1200, 2100, "CA2", "B9987", "B9987 de", "B9987 ar", 24.9, "414L", "B737", TIME_DICT]
    )
    inst_4 = IntervalBase(
        [900, 0, 900, "CA3", "B9987", "B9988 de", "B9988 ar", 24.9, "414", "B737", TIME_DICT]
    )
    inst_5 = IntervalBase(
        [900, 1200, 2100, "CA4", "B9987", "B9989 de", "B9989 ar", 24.9, "415", "B737", TIME_DICT]
    )
    inst_6 = IntervalBase(
        [900, 1200, 2100, "CA5", "B9990", "B9989 de", "B9989 ar", 24.9, "415L", "B737", TIME_DICT]
    )

    instance_list = [inst_1, inst_2, inst_3, inst_4, inst_5, inst_6]
    original_list = GetInterval(filename="../data\\mock_231029.csv").interval
    min_inst, max_inst = IncreaseFlight(original_list)._get_index_range(inst_3, 2, instance_list)
    assert min_inst.airline == inst_2.airline
    assert max_inst.airline == inst_5.airline


def test_aircraft_model():
    # Test cases for "RH" (assuming it represents another type, e.g., Heavy)
    model = "A330"
    assert AircraftModel(model).aircraft_type == "H"

    model = "B747"
    assert AircraftModel(model).aircraft_type == "H"

    # Test cases for "TM" (assuming it represents another type)
    model = "AT42"
    assert AircraftModel(model).aircraft_type == "M"

    model = "DH8C"
    assert AircraftModel(model).aircraft_type == "M"

    # Test cases for "TL" (assuming it represents another type)
    model = "B190"
    assert AircraftModel(model).aircraft_type == "L"

    model = "SW4"
    assert AircraftModel(model).aircraft_type == "L"


def test_wake_turbulence():
    # Dummy data for the first 9 elements in the info_list
    dummy_data = [0, 0, 0, "airline", "registration", "begin_callsign", "end_callsign", 0, "gate"]

    # Test case 1: Front aircraft is Light
    assert get_wake_turbulence(IntervalBase(dummy_data + ["B190", TIME_DICT]),
                               IntervalBase(dummy_data + ["SW4", TIME_DICT])) == 60
    assert get_wake_turbulence(IntervalBase(dummy_data + ["Y12", TIME_DICT]),
                               IntervalBase(dummy_data + ["GLEX", TIME_DICT])) == 60
    assert get_wake_turbulence(IntervalBase(dummy_data + ["MA60", TIME_DICT]),
                               IntervalBase(dummy_data + ["EA30", TIME_DICT])) == 60

    # Test case 2: Front aircraft is Medium
    assert get_wake_turbulence(IntervalBase(dummy_data + ["FK70", TIME_DICT]),
                               IntervalBase(dummy_data + ["BA31", TIME_DICT])) == 120
    assert get_wake_turbulence(IntervalBase(dummy_data + ["GLEX", TIME_DICT]),
                               IntervalBase(dummy_data + ["CL35", TIME_DICT])) == 60
    assert get_wake_turbulence(IntervalBase(dummy_data + ["LJ60", TIME_DICT]),
                               IntervalBase(dummy_data + ["CONC", TIME_DICT])) == 60

    # Test case 3: Front aircraft is Heavy
    assert get_wake_turbulence(IntervalBase(dummy_data + ["A340", TIME_DICT]),
                               IntervalBase(dummy_data + ["BE10", TIME_DICT])) == 180
    assert get_wake_turbulence(IntervalBase(dummy_data + ["A330", TIME_DICT]),
                               IntervalBase(dummy_data + ["BE02", TIME_DICT])) == 90
    assert get_wake_turbulence(IntervalBase(dummy_data + ["A30B", TIME_DICT]),
                               IntervalBase(dummy_data + ["B77W", TIME_DICT])) == 90


def test_find_insertion_location():
    # 构建一些 IntervalBase 实例
    dummy_data = [0, 13000, 24000, "airline", "registration", "begin_callsign", "end_callsign", 0, "gate"]
    inst1 = IntervalBase(dummy_data + ["B190", TIME_DICT])  # 轻型飞机, 开始时间为 10
    inst2 = IntervalBase([0, 27340, 34530] + dummy_data[3:] + ["FK70", TIME_DICT])  # 中型飞机, 开始时间为 20
    inst3 = IntervalBase([0, 34670, 43450] + dummy_data[3:] + ["A340", TIME_DICT])  # 重型飞机, 开始时间为 30

    useful_interval = [inst1, inst2, inst3]

    # 测试用例 1: 无冲突情况
    test_inst = IntervalBase([0, 54560, 66750] + dummy_data[3:] + ["LJ60", TIME_DICT])  # 插入时间在所有飞机之后
    origin_test_inst = deepcopy(test_inst)
    assert find_insertion_location(useful_interval, test_inst).begin_interval == origin_test_inst.begin_interval

    # 测试用例 2: 有冲突情况
    test_inst_conflict = IntervalBase([0, 13000, 24000] + dummy_data[3:] + ["A330", TIME_DICT])  # 插入时间和 inst1 冲突
    origin_test_inst_conflict = deepcopy(test_inst_conflict)
    # 应该返回一个调整后的 inst，不是 test_inst_conflict
    assert find_insertion_location(useful_interval,
                                   test_inst_conflict).begin_interval != origin_test_inst_conflict.begin_interval


def test_all():
    original_list = GetInterval(filename="../data\\mock_231029.csv").interval
    increase_list = IncreaseFlight(original_list).increase_flight()
    OutPut(increase_list, filename="../data\\mock_231029.csv")
