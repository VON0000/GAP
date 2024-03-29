import re

import gurobipy

from BasicFunction.AirlineType import AirlineType
from BasicFunction.GetInterval import GetInterval
from BasicFunction.GetWingSpan import GetWingSpan
from BasicFunction.IntervalType import IntervalBase
from FlightIncrease.IncreaseFlight import is_overlapping
from refactorGateAllocation.GetTaxiingTime import GetTaxiingTime
from refactorGateAllocation.RemoteGate import REMOTE_GATE


class GateAllocation:
    def __init__(self, data: dict, seuil: int, pattern: str, quarter: int = 0):
        self.quarter = quarter
        self.pattern = pattern
        self.interval = GetInterval(data, self.quarter, seuil).transform_second_to_half_minute()
        self.available_gate_dict = _available_gate_dict(self.interval)
        self.model = gurobipy.Model()

    def optimization(self) -> dict:
        self.get_variable()
        self.get_constraints()
        self.get_objective()
        self.model.optimize()
        result = self.get_result()

        return result

    def get_result(self) -> dict:
        """
        优化完成后返回结果
        """
        result = {}
        for inst in self.interval:
            for ag in self.available_gate_dict[inst]:
                if self.model.getVarByName(f"x_{inst}_{ag}").X == 1:
                    result[inst] = ag

        return result

    def get_variable(self):
        for inst in self.interval:
            for ag in self.available_gate_dict[inst]:
                self.model.addVar(vtype=gurobipy.GRB.BINARY, name=f"x_{inst}_{ag}")

        self.model.update()

    def get_constraints(self):
        for inst in self.interval:
            # 每个 interval 只能分配一个 gate
            self.model.addConstr(
                gurobipy.quicksum(
                    self.model.getVarByName(f"x_{inst}_{ag}") for ag in self.available_gate_dict[inst]
                ) == 1,
                name=f"constraint_{inst}"
            )
            for ref_inst in get_conflicts(inst, self.interval):
                for ag in self.available_gate_dict[inst]:
                    # 414 和 414R 414L 414 不能同时分配
                    if not (("L" in ag) or ("R" in ag)):
                        # ag = 414 时， re.findall(r"\d+", ag) = ['414']， 因此 rag = 414R 414L 414 会被选中
                        # ag = 601 时， re.findall(r"\d+", ag) = ['601']， 因此 rag = 601 会被选中
                        conflict_gate = [rag for rag in self.available_gate_dict[ref_inst] if
                                         re.findall(r"\d+", ag) == re.findall(r"\d+", rag)]
                        self._conflict_in_dependent_gate(conflict_gate, inst, ref_inst, ag)
                    # 414L 414R
                    else:
                        # ag = 414L 时， re.findall(r"\d+", ag) = ['414']， 因此 rag = 414L 414 会被选中
                        conflict_gate = [rag for rag in self.available_gate_dict[ref_inst] if
                                         (re.findall(r"\d+", ag) == [rag] or ag == rag)]
                        self._conflict_in_dependent_gate(conflict_gate, inst, ref_inst, ag)

        self.model.update()

    def _conflict_in_dependent_gate(self, conflict_gate: list, inst: IntervalBase, ref_inst: IntervalBase, ag: str):
        for rag in conflict_gate:
            self.model.addConstr(
                self.model.getVarByName(f"x_{inst}_{ag}") + self.model.getVarByName(
                    f"x_{ref_inst}_{rag}") <= 1,
                name=f"constraint_{inst}_{ref_inst}_{ag}_{rag}"
            )

    def get_objective(self):
        """
        滑行时间 + 远机位代价
        """
        self.model.setObjective(
            gurobipy.quicksum(
                self._get_taxiing_time(inst, ag) * self.model.getVarByName(f"x_{inst}_{ag}") for inst in self.interval
                for ag in self.available_gate_dict[inst]
            ) + gurobipy.quicksum(
                self._get_remote_cost(inst, ag) * self.model.getVarByName(f"x_{inst}_{ag}") for inst in self.interval
                for ag in self.available_gate_dict[inst]
            ), gurobipy.GRB.MINIMIZE
        )

        self.model.update()

    def _get_taxiing_time(self, inst: IntervalBase, ag: str) -> float:
        if inst.begin_callsign == inst.end_callsign:
            return GetTaxiingTime(ag, self.pattern).taxiing_time[inst.begin_qfu]
        return GetTaxiingTime(ag, self.pattern).taxiing_time[inst.end_qfu] + \
            GetTaxiingTime(ag, self.pattern).taxiing_time[inst.begin_qfu]

    @staticmethod
    def _get_remote_cost(inst: IntervalBase, ag: str) -> float:
        if ag not in REMOTE_GATE:
            return 0

        alpha = 1000 * 1000
        if ag in AirlineType(inst.airline).available_gate:
            return alpha
        return alpha * 10


def get_conflicts(inst: IntervalBase, interval: list) -> list:
    """
    找到和 inst 会产生冲突的 interval
    两个实例的 [begin_interval, end_interval] 有交集则产生冲突
    """
    ref_inst_list = []
    for ref_inst in interval:
        if ref_inst == inst:
            continue

        if is_overlapping(
                (ref_inst.begin_interval, ref_inst.end_interval),
                (inst.begin_interval, inst.end_interval)
        ):
            ref_inst_list.append(ref_inst)

    return ref_inst_list


def _available_gate_dict(interval: list) -> dict:
    available_gate_dict = {}
    for inst in interval:
        gate_list = get_available_gate(inst)
        available_gate_dict[inst] = gate_list

    return available_gate_dict


def get_available_gate(inst: IntervalBase) -> list:
    if AirlineType(inst.airline).type == "domestic":
        available_gate_list = list(set(AirlineType(inst.airline).available_gate) | set(REMOTE_GATE))
    else:
        available_gate_list = AirlineType(inst.airline).available_gate

    available_gate_list = [g for g in available_gate_list if inst.wingspan <= GetWingSpan(g).size]

    return available_gate_list
