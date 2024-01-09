import loguru
import numpy as np

from FlightIncrease import OutPut
from FlightIncrease.AirlineType import get_airline_info, AirlineType, get_group_dict
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
        [900, 1800, 2700, "CA0", "B9985", "B9985 de", "B9985 ar", 24.9, "414"]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "CA1", "B9987", "B9986 de", "B9986 ar", 24.9, "414R"]
    )
    inst_3 = IntervalBase(
        [900, 1200, 2100, "CA2", "B9987", "B9987 de", "B9987 ar", 24.9, "414L"]
    )
    inst_4 = IntervalBase(
        [900, 0, 900, "CA3", "B9987", "B9988 de", "B9988 ar", 24.9, "414"]
    )
    inst_5 = IntervalBase(
        [900, 1200, 2100, "CA4", "B9987", "B9989 de", "B9989 ar", 24.9, "415"]
    )
    inst_6 = IntervalBase(
        [900, 1200, 2100, "CA5", "B9990", "B9989 de", "B9989 ar", 24.9, "415L"]
    )

    instance_list = [inst_1, inst_2, inst_3, inst_4, inst_5, inst_6]
    min_inst, max_inst = IncreaseFlight(filename="../data\\mock_231029.csv")._get_index_range(inst_3, 2, instance_list)
    assert min_inst.airline == inst_2.airline
    assert max_inst.airline == inst_5.airline


def test_all():
    increase_list = IncreaseFlight(filename="../data\\mock_231029.csv").increase_flight()
    OutPut(increase_list, filename="../data\\mock_231029.csv")
