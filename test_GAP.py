import math
import re

import pandas as pd

from BasicFunction.AirlineType import AirlineType
from BasicFunction.GetData import get_data
from BasicFunction.GetInterval import GetInterval
from BasicFunction.GetAircraftTide import AircraftTide
from BasicFunction.GetGateAttribute import GetGateAttribute
from BasicFunction.IntervalType import IntervalBase
from GateAllocation.GateAllocation import get_available_gate, get_conflicts, GateAllocation
from GateAllocation.GetTaxiingTime import get_all_taxiing_time, GetTaxiingTime
from GateAllocation.OutPut import OutPut
from GateAllocation.RemoteGate import REMOTE_GATE
from GateAllocation.reAllocation import get_fixed_result, fixed_result, find_group, cost_for_international, \
    cost_for_domestic, cost_for_cargo, change_end_interval, ReAllocation, get_fixed_inst

HOUR = 60 * 60
TIME_DICT = {"ar": {"TTOT": 0, "TLDT": 0, "ATOT": 0, "ALDT": 0},
             "de": {"TTOT": 0, "TLDT": 0, "ATOT": 0, "ALDT": 0}}


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
    data = get_data("data/mock_231029.csv")
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
    time_list = AircraftTide(data=get_data("data/mock_231029.csv"), quarter=12, seuil=28)._get_time_used(quarter=12)
    assert 12840 in time_list
    assert 9420 in time_list

    assert 35880 not in time_list
    assert 41520 not in time_list

    time_list = AircraftTide(data=get_data("data/mock_231029.csv"), quarter=50, seuil=28)._get_time_used(quarter=50)
    assert 35880 in time_list
    assert 41520 in time_list


def test_get_interval():
    data = get_data("data/mock_231029.csv")
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
            assert i.begin_qfu == "ARR-16R"
        if i.begin_callsign == "CSC8861 ar":
            print("reach\n")
            assert i.begin_qfu == "ARR-16R"


def test_get_available_gate():
    inst_1 = IntervalBase(
        [900, 1800, 2700, "NokScoot", "B9985", "B9985 de", "B9985 ar", 60, "414", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "SENDI", "B9986", "B9986 de", "B9986 ar", 24.9, "414R", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_3 = IntervalBase(
        [900, 1200, 2100, "Chinaexpressair", "B9987", "B9987 de", "B9987 ar", 24.9, "414L", "B737", TIME_DICT] + [
            "DEP-16R"]
    )
    assert get_available_gate(inst_1) == ["101", "102", "105"]
    assert sorted(get_available_gate(inst_2)) == sorted(["110", "111", "112", "113", "114", "115", "116"] + REMOTE_GATE)
    assert sorted(get_available_gate(inst_3)) == sorted(REMOTE_GATE)


def test_get_wing_size():
    all_gate = pd.read_excel("./data/wingsizelimit.xls", sheet_name=None)
    sheet_data = all_gate["sheet1"]
    gate_size = sheet_data.to_dict(orient="list")
    for i in range(len(gate_size["gate"])):
        assert GetGateAttribute(str(gate_size["gate"][i])).size == gate_size["size_limit"][i]
    assert GetGateAttribute("104").size == 52


def test_get_conflicts():
    inst_1 = IntervalBase(
        [900, 1800, 2700, "CA0", "B9985", "B9985 de", "B9985 ar", 24.9, "414", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "CA1", "B9987", "B9986 de", "B9986 ar", 24.9, "414R", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_3 = IntervalBase(
        [900, 2600, 3400, "CA2", "B9987", "B9987 de", "B9987 ar", 24.9, "414L", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_4 = IntervalBase(
        [900, 0, 900, "CA3", "B9987", "B9988 de", "B9988 ar", 24.9, "414", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_5 = IntervalBase(
        [900, 1900, 2500, "CA4", "B9987", "B9989 de", "B9989 ar", 24.9, "415", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_6 = IntervalBase(
        [900, 2900, 3600, "CA5", "B9990", "B9989 de", "B9989 ar", 24.9, "415L", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_7 = IntervalBase(
        [900, 1600, 2900, "CA6", "B9990", "B9989 de", "B9989 ar", 24.9, "415L", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_list = [inst_1, inst_2, inst_3, inst_4, inst_5, inst_6, inst_7]

    assert get_conflicts(inst_1, inst_list) == [inst_2, inst_3, inst_5, inst_7]


def test_get_taxiing_time_gate_allocation():
    def _get_taxiing_time(inst: IntervalBase, ag: str, pattern: str) -> float:
        if inst.begin_callsign == inst.end_callsign:
            return GetTaxiingTime(ag, pattern).taxiing_time[inst.begin_qfu]
        return GetTaxiingTime(ag, pattern).taxiing_time[inst.end_qfu] + \
            GetTaxiingTime(ag, pattern).taxiing_time[inst.begin_qfu]

    inst_1 = IntervalBase(
        [900, 1800, 2700, "CA0", "B9985", "B9985 de", "B9985 de", 24.9, "414", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "CA1", "B9987", "B9986 ar", "B9986 ar", 24.9, "414R", "B737", TIME_DICT] + ["ARR-16L"]
    )
    inst_3 = IntervalBase(
        [900, 2600, 3400, "CA2", "B9987", "B9987 ar", "B9987 de", 24.9, "414L", "B737", TIME_DICT] + ["ARR-16L",
                                                                                                      "DEP-16R"]
    )
    assert _get_taxiing_time(inst_1, "112", "MIN") == 465
    assert _get_taxiing_time(inst_2, "415", "PN_MANEX") == 525
    assert _get_taxiing_time(inst_3, "896", "MANEX") == 980


def test_get_constraints():
    gate_list = ["414", "414R", "414L", "601", "610"]

    def get_conflict(gate):
        if not (("L" in gate) or ("R" in gate)):
            conflict_gate = [g for g in gate_list if re.findall(r"\d+", gate) == re.findall(r"\d+", g)]
        else:
            conflict_gate = [g for g in gate_list if (re.findall(r"\d+", gate) == [g] or gate == g)]

        return conflict_gate

    assert get_conflict("414") == ["414", "414R", "414L"]
    assert get_conflict("414R") == ["414", "414R"]
    assert get_conflict("601") == ["601"]


def test_get_remote_cost():
    def _get_remote_cost(inst: IntervalBase, ag: str) -> float:
        if ag not in REMOTE_GATE:
            return 0

        alpha = 1000 * 1000
        if ag in AirlineType(inst.airline).available_gate:
            return alpha
        return alpha * 10

    inst_1 = IntervalBase(
        [900, 1200, 2100, "SENDI", "B9986", "B9986 de", "B9986 ar", 24.9, "414R", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "LUCKYAIR", "B9986", "B9986 de", "B9986 ar", 24.9, "414R", "B737", TIME_DICT] + ["DEP-16R"]
    )
    assert _get_remote_cost(inst_1, "415L") == 1000 * 1000 * 10
    assert _get_remote_cost(inst_2, "415L") == 1000 * 1000
    assert _get_remote_cost(inst_2, "110") == 0


def test_gate_allocation():
    data = get_data("data/error-in-data/gaptraffic-2017-08-03-new.csv")
    GateAllocation(data, 28, "MANEX").optimization()


def test_get_fixed_result():
    inst_1 = IntervalBase(
        [900, 1800, 2700, "CA0", "B9985", "B9985 de", "B9985 ar", 24.9, "414", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_2 = IntervalBase(
        [900, 1200, 2100, "CA1", "B9987", "B9986 de", "B9986 ar", 24.9, "414R", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_3 = IntervalBase(
        [900, 2600, 3400, "CA2", "B9987", "B9987 de", "B9987 ar", 24.9, "414L", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_list = {
        inst_1: "414",
        inst_2: "414R",
        inst_3: "414L"
    }
    key = get_fixed_inst(inst_1, inst_list, "de")
    assert inst_list[key[0]] == "414"
    key = get_fixed_inst(inst_2, inst_list, "de")
    assert inst_list[key[0]] == "414R"
    key = get_fixed_inst(inst_3, inst_list, "de")
    assert inst_list[key[0]] == "414L"


def test_fixed_result():
    time_dict = {"ar": {"TTOT": 27000, "TLDT": 30000, "ATOT": 36000, "ALDT": 45000},
                 "de": {"TTOT": 27000, "TLDT": 30000, "ATOT": 36000, "ALDT": 45000}}
    inst_1 = IntervalBase(
        [9000, 36000, 45000, "CA0", "B9985", "B9985 ar", "B9985 de", 24.9, "414", "B737", time_dict] + ["DEP-16R"]
    )
    inst_2 = IntervalBase(
        [9000, 36000, 45000, "CA1", "B9987", "B9986 ar", "B9986 ar", 24.9, "414R", "B737", time_dict] + ["DEP-16R"]
    )
    inst_3 = IntervalBase(
        [9000, 36000, 45000, "CA2", "B9987", "B9987 de", "B9987 de", 24.9, "414L", "B737", time_dict] + ["DEP-16R"]
    )
    inst_list = {
        inst_1: "414",
        inst_2: "414R",
        inst_3: "414L"
    }
    assert fixed_result(inst_1, 30, inst_list) is None
    assert fixed_result(inst_1, 50, inst_list) == "414"
    assert fixed_result(inst_2, 36, inst_list) is None
    assert fixed_result(inst_2, 50, inst_list) == "414R"
    assert fixed_result(inst_3, 30, inst_list) is None
    assert fixed_result(inst_3, 50, inst_list) == "414L"


def test_find_group():
    assert find_group("105") == "TERMINAL_ONE"
    assert find_group("230") == "TERMINAL_TWO"
    assert find_group("417") == "REMOTE_ONE"
    assert find_group("610") == "REMOTE_TWO"


def test_cost_for_international():
    assert cost_for_international("105", "105", 1000 * 1000) == 0
    assert cost_for_international("105", "101", 1000 * 1000) == 1000 * 1000


def test_cost_for_cargo():
    assert cost_for_cargo("876", "876", 1000 * 1000) == 0
    assert cost_for_cargo("888", "902", 1000 * 1000) == 10 * 1000 * 1000


def test_cost_for_domestic():
    assert cost_for_domestic("417", "101", "105", 1000 * 1000) == 100 * 1000 * 1000
    assert cost_for_domestic("110", "101", "204", 1000 * 1000) == 10 * 1000 * 1000
    assert cost_for_domestic("110", "101", "105", 1000 * 1000) == 1000 * 1000
    assert cost_for_domestic("110", "101", "110", 1000 * 1000) == 0
    assert cost_for_domestic("105", "206", "607", 1000 * 1000) == 0
    assert cost_for_domestic("607", "206", "607", 1000 * 1000) == 1 * 1000 * 1000
    assert cost_for_domestic("419", "206", "607", 1000 * 1000) == 10 * 1000 * 1000
    assert cost_for_domestic("417", "601", "417", 1000 * 1000) == 0
    assert cost_for_domestic("105", "601", "417", 1000 * 1000) == 1 * 1000 * 1000
    assert cost_for_domestic("418", "601", "417", 1000 * 1000) == 10 * 1000 * 1000


def test_get_move_cost_reAllocation():
    def _get_move_cost(inst: IntervalBase, ag: str, init_results: dict, last_results: dict) -> float:
        alpha = 1000 * 1000
        init_gate = get_fixed_result(init_results, get_fixed_inst(inst, init_results, inst.begin_callsign[-2:]))
        last_gate = get_fixed_result(last_results, get_fixed_inst(inst, last_results, inst.begin_callsign[-2:]))

        if AirlineType(inst.airline).type == "international":
            return cost_for_international(ag, last_gate, alpha)

        if AirlineType(inst.airline).type == "cargo":
            return cost_for_cargo(ag, last_gate, alpha)

        return cost_for_domestic(ag, init_gate, last_gate, alpha)

    inst_1 = IntervalBase(
        [9000, 36000, 45000, "SHUNFENG", "B9985", "B9985 de", "B9985 ar", 24.9, "888", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_2 = IntervalBase(
        [9000, 36000, 45000, "STRAITAIR", "B9987", "B9986 ar", "B9986 ar", 24.9, "415", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_3 = IntervalBase(
        [9000, 36000, 45000, "EVAAir", "B9987", "B9987 de", "B9987 de", 24.9, "106", "B737", TIME_DICT] + ["DEP-16R"]
    )
    last = {
        inst_1: "888",
        inst_2: "415",
        inst_3: "106"
    }
    init = {
        inst_1: "901",
        inst_2: "206",
        inst_3: "101"
    }
    assert _get_move_cost(inst_1, "901", init, last) == 10 * 1000 * 1000
    assert _get_move_cost(inst_2, "607", init, last) == 10 * 1000 * 1000
    assert _get_move_cost(inst_3, "101", init, last) == 1000 * 1000


def test_change_end_interval():
    inst_1 = IntervalBase(
        [9000, 36000, 45000, "SHUNFENG", "B9985", "B9985 de", "B9985 ar", 24.9, "888", "B737", TIME_DICT] + ["DEP-16R"]
    )
    inst_2 = IntervalBase(
        [18000, 40000, 58000, "STRAITAIR", "B9987", "B9986 ar", "B9986 ar", 24.9, "415", "B737", TIME_DICT] + ["DEP-16R"]
    )

    before = id(inst_1)
    change_end_interval(inst_1, inst_2)
    after = id(inst_1)

    assert inst_1.interval == 18000
    assert inst_1.end_interval == 58000
    assert before == after


def test_reallocation():
    data = get_data("data/error-in-data/gaptraffic-2017-08-03-new.csv")
    init_result = GateAllocation(data, 28, "MANEX").optimization()

    quarter = 0
    last_result = init_result
    result_list = []
    while quarter < 10:
        last_result = ReAllocation(data, 0, "MANEX", quarter, init_result, last_result).optimization()
        result_list.append(last_result)

        quarter += 1

    OutPut(data, "data\\mock_231029.csv", "./results/Traffic_GAP_test\\").output_process(result_list)
    OutPut(data, "data\\mock_231029.csv", "./results/Traffic_GAP_test\\").output_final(last_result)
