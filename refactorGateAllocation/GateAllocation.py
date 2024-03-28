import re
from typing import Union

import gurobipy

from BasicFunction.AirlineType import AirlineType
from BasicFunction.GetInterval import GetInterval
from BasicFunction.GetWingSpan import GetWingSpan
from BasicFunction.IntervalType import IntervalBase
from FlightIncrease.IncreaseFlight import _is_overlapping
from refactorGateAllocation.RemoteGate import REMOTE_GATE


class GateAllocation:
    def __init__(self, data: dict, seuil: int, quarter: int = 0):
        self.quarter = quarter
        self.interval = GetInterval(data, self.quarter, seuil).interval
        self.available_gate_dict = self.available_gate_dict()
        self.model = gurobipy.Model()

    def available_gate_dict(self) -> dict:
        available_gate_dict = {}
        for inst in self.interval:
            if not ignore_inst(inst, self.quarter):
                continue
            gate_list = get_available_gate(inst)
            available_gate_dict[inst] = gate_list

        return available_gate_dict

    def optimization(self):
        ...

    def get_variable(self):
        for inst in self.interval:
            for ag in self.available_gate_dict[inst]:
                self.model.addVar(vtype=gurobipy.GRB.BINARY, name=f"x_{inst}_{ag}")

    def get_constraints(self):
        for inst in self.interval:
            # 每个 interval 只能分配一个 gate
            self.model.addConstr(
                gurobipy.quicksum(
                    self.model.getVarByName(f"x_{inst}_{ag}") for ag in self.available_gate_dict[inst]
                ) == 1,
                name=f"constraint_{inst}"
            )
            for ref_inst in self.get_conflicts(inst):
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
                                         (re.findall(r"\d+", ag) == rag or ag == rag)]
                        self._conflict_in_dependent_gate(conflict_gate, inst, ref_inst, ag)

    def _conflict_in_dependent_gate(self, conflict_gate: list, inst: IntervalBase, ref_inst: IntervalBase, ag: str):
        for rag in conflict_gate:
            self.model.addConstr(
                self.model.getVarByName(f"x_{inst}_{ag}") + self.model.getVarByName(
                    f"x_{ref_inst}_{rag}") <= 1,
                name=f"constraint_{inst}_{ref_inst}_{ag}_{rag}"
            )

    def get_objective(self):
        ...

    def get_conflicts(self, inst: IntervalBase) -> list:
        """
        找到和 inst 会产生冲突的 interval
        两个实例的 [begin_interval, end_interval] 有交集则产生冲突
        """
        ref_inst_list = []
        for ref_inst in self.interval:
            if _is_overlapping(
                    (ref_inst.begin_interval, ref_inst.end_interval),
                    (inst.begin_interval, inst.end_interval)
            ):
                ref_inst_list.append(ref_inst)

        return ref_inst_list


def ignore_inst(inst: IntervalBase, quarter: int) -> Union[IntervalBase, None]:
    """
    如果 inst 的 target 时间在 quarter 之前， actual 时间在 quarter + 一小时 之后，则忽略当前 inst 返回 None
    """
    ...


def get_available_gate(inst: IntervalBase) -> list:
    if AirlineType(inst.airline).type == "domestic":
        available_gate_list = AirlineType(inst.airline).available_gate + REMOTE_GATE
    else:
        available_gate_list = AirlineType(inst.airline).available_gate

    for g in available_gate_list:
        if inst.wingspan > GetWingSpan(g).size:
            available_gate_list.remove(g)

    return available_gate_list
