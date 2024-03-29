from typing import Union

import gurobipy

from BasicFunction.AirlineType import AirlineType
from BasicFunction.IntervalType import IntervalBase
from refactorGateAllocation.GateAllocation import GateAllocation

TERMINAL_ONE = ["101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111", "112", "113",
                "114", "115", "116", "117", "118"]
TERMINAL_TWO = ["201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", "212", "213",
                "214", "215", "216", "217", "218", "219", "220", "221", "222", "223", "224", "225", "226",
                "227", "228", "229", "230"]
REMOTE_ONE = ["409", "410", "411", "412", "413", "414", "415", "416", "417", "418", "419", "414L", "414R",
              "415L", "415R", "416L", "416R", "417L", "417R", "418L", "418R", "419L", "419R"]
REMOTE_TWO = ["601", "602", "603", "604", "605", "606", "607", "608", "609", "610"]

GROUP_DICT = {
    "TERMINAL_ONE": TERMINAL_ONE,
    "TERMINAL_TWO": TERMINAL_TWO,
    "REMOTE_ONE": REMOTE_ONE,
    "REMOTE_TWO": REMOTE_TWO
}


class ReAllocation(GateAllocation):
    def __init__(self, data: dict, seuil: int, pattern: str, quarter: int, init_results: dict, last_results: dict):
        super().__init__(data, seuil, pattern, quarter)
        self.init_results = init_results
        self.last_results = last_results

    def get_variable(self):
        for inst in self.interval:
            fix_gate = fixed_result(inst, self.quarter, self.last_results)
            if fix_gate:
                self.model.addVar(vtype=gurobipy.GRB.BINARY, name=f"x_{inst}_{fix_gate}")
                self.available_gate_dict[inst] = [fix_gate]
            else:
                for ag in self.available_gate_dict[inst]:
                    self.model.addVar(vtype=gurobipy.GRB.BINARY, name=f"x_{inst}_{ag}")

        self.model.update()

    def get_objective(self):
        self.model.setObjective(
            gurobipy.quicksum(
                self._get_taxiing_time(inst, ag) * self.model.getVarByName(f"x_{inst}_{ag}") for inst in self.interval
                for ag in self.available_gate_dict[inst]
            ) + gurobipy.quicksum(
                self._get_move_cost(inst, ag) * self.model.getVarByName(f"x_{inst}_{ag}") for inst in self.interval
                for ag in self.available_gate_dict[inst]
            ), gurobipy.GRB.MINIMIZE
        )

        self.model.update()

    def _get_move_cost(self, inst: IntervalBase, ag: str) -> float:
        alpha = 1000 * 1000
        init_gate = get_fixed_result(self.init_results,
                                     get_fixed_inst(inst, self.init_results, inst.begin_callsign[-2:]))
        last_gate = get_fixed_result(self.last_results,
                                     get_fixed_inst(inst, self.last_results, inst.begin_callsign[-2:]))

        if AirlineType(inst.airline).type == "international":
            return cost_for_international(ag, last_gate, alpha)

        if AirlineType(inst.airline).type == "cargo":
            return cost_for_cargo(ag, last_gate, alpha)

        return cost_for_domestic(ag, init_gate, last_gate, alpha)


def cost_for_international(ag: str, last_gate: str, alpha: int) -> float:
    if ag == last_gate:
        return 0
    return 1 * alpha


def cost_for_cargo(ag: str, last_gate: str, alpha: int) -> float:
    if ag == last_gate:
        return 0
    return 10 * alpha


def cost_for_domestic(ag: str, init_gate: str, last_gate: str, alpha: int) -> float:
    if find_group(last_gate) == "TERMINAL_ONE" or find_group(last_gate) == "TERMINAL_TWO":
        if ag == last_gate:
            return 0
        if ag in GROUP_DICT[find_group(last_gate)]:
            return 1 * alpha
        if ag in GROUP_DICT["REMOTE_ONE"] or ag in GROUP_DICT["REMOTE_TWO"]:
            return 100 * alpha
        return 10 * alpha

    if find_group(init_gate) == "TERMINAL_ONE" or find_group(init_gate) == "TERMINAL_TWO":
        if ag in GROUP_DICT["TERMINAL_ONE"] or ag in GROUP_DICT["TERMINAL_TWO"]:
            return 0
        if ag == last_gate:
            return 1 * alpha
        else:
            return 10 * alpha

    if ag == last_gate:
        return 0
    if ag in GROUP_DICT["TERMINAL_ONE"] or ag in GROUP_DICT["TERMINAL_TWO"]:
        return 1 * alpha
    return 10 * alpha


def find_group(ag: str):
    """
    遍历 GROUP_DICT，找到 ag 所在的 list
    """
    list_found = None
    for list_name, the_list in GROUP_DICT.items():
        if ag in the_list:
            list_found = list_name
            break

    return list_found


def fixed_result(inst: IntervalBase, quarter: int, last_results: dict) -> Union[None, str]:
    """
    如果 inst 在当前时间 + 30minutes 这个时刻之前，返回之前迭代得到的机位（固定机位）
    """
    result = None
    if inst.begin_callsign == inst.end_callsign:
        inst_type = inst.begin_callsign[-2:]
        if inst_type == "de" and inst.time_dict[inst_type] == {}:
            print(inst)
        if inst_type == "de" and inst.time_dict[inst_type]["ATOT"] < quarter * 15 * 60 + 30 * 60:
            ref_inst = get_fixed_inst(inst, last_results, inst_type)
            change_end_interval(inst, ref_inst[0])
            result = get_fixed_result(last_results, ref_inst)
        if inst_type == "ar" and inst.time_dict[inst_type]["ALDT"] < quarter * 15 * 60 + 30 * 60:
            ref_inst = get_fixed_inst(inst, last_results, inst_type)
            change_end_interval(inst, ref_inst[0])
            result = get_fixed_result(last_results, ref_inst)
    else:
        if inst.time_dict[inst.begin_callsign[-2:]]["ALDT"] < quarter * 15 * 60 + 30 * 60:
            ref_inst = get_fixed_inst(inst, last_results, inst.begin_callsign[:2])
            change_end_interval(inst, ref_inst[0])
            result = get_fixed_result(last_results, ref_inst)
        if inst.time_dict[inst.end_callsign[-2:]]["ATOT"] < quarter * 15 * 60 + 30 * 60:
            ref_inst = get_fixed_inst(inst, last_results, inst.end_callsign[:2])
            change_end_interval(inst, ref_inst[0])
            result = get_fixed_result(last_results, ref_inst)
    return result


def get_fixed_inst(inst: IntervalBase, last_results: dict, inst_type: str) -> list:
    """
    从过去的结果中找到 inst 对应的实例
    """
    result = []
    for key in last_results:
        if inst_type == "ar":
            if (key.registration == inst.registration) and (key.begin_callsign == inst.begin_callsign):
                result.append(key)
        else:
            if (key.registration == inst.registration) and (key.end_callsign == inst.end_callsign):
                result.append(key)

    assert result is None or len(result) == 1
    return result


def get_fixed_result(last_results: dict, ref_inst: list) -> str:
    """
    从 ref_inst 中找到 inst 对应的机位
    """
    return last_results[ref_inst[0]]


def change_end_interval(inst: IntervalBase, key: IntervalBase):
    """
    将 key 的属性赋值给 inst
    """
    for attr, value in key.__dict__.items():
        setattr(inst, attr, value)
