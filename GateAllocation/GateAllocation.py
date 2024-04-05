import time
from typing import Callable

import gurobipy

from BasicFunction.AirlineType import AirlineType
from BasicFunction.AvailableGateStrategy import get_available_gate_GAP
from BasicFunction.GetInterval import GetInterval
from BasicFunction.GetGateAttribute import GetGateAttribute
from BasicFunction.IntervalType import IntervalBase
from FlightIncrease.IncreaseFlight import is_overlapping
from GateAllocation.GetTaxiingTime import GetTaxiingTime
from GateAllocation.RemoteGate import REMOTE_GATE


class GateAllocation:
    def __init__(self, data: dict, seuil: int, pattern: str, quarter: int = 0,
                 available_gate_strategy: Callable[[IntervalBase], list] = get_available_gate_GAP):
        self.quarter = quarter
        self.pattern = pattern
        self.interval = GetInterval(data, self.quarter, seuil).transform_second_to_half_minute()
        self.conflict_dict = {}
        self.available_gate_dict = _available_gate_dict(self.interval, available_gate_strategy)
        self.model = gurobipy.Model()

    def optimization(self) -> dict:
        t1 = time.time()

        t3 = time.time()
        self.get_variable()
        t4 = time.time()
        print("载入变量耗时:%s秒" % (t4 - t3))

        t5 = time.time()
        self.conflict_dict = self._get_conflicts_dict()
        self.get_constraints()
        t6 = time.time()
        print("载入限制条件耗时:%s秒" % (t6 - t5))

        t7 = time.time()
        self.get_objective()
        t8 = time.time()
        print("载入优化目标耗时:%s秒" % (t8 - t7))

        t9 = time.time()
        self.model.optimize()
        t10 = time.time()
        print("优化耗时:%s秒" % (t10 - t9))

        if self.model.status == gurobipy.GRB.INFEASIBLE:
            self.model.computeIIS()
            return {}

        result = self.get_result()
        t2 = time.time()
        print('程序运行时间:%s秒' % (t2 - t1))

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
            for ref_inst in self.conflict_dict[inst]:
                for ag in self.available_gate_dict[inst]:
                    conflict_gate = list(
                        set(GetGateAttribute(ag).dependent_gate) & set(self.available_gate_dict[ref_inst]))
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

    def _get_conflicts_dict(self) -> dict:
        conflict_dict = {}
        for inst in self.interval:
            ref_inst_list = get_conflicts(inst, self.interval)
            conflict_dict[inst] = ref_inst_list
        return conflict_dict


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


def _available_gate_dict(interval: list, available_gate_strategy: Callable[[IntervalBase], list]) -> dict:
    available_gate_dict = {}
    for inst in interval:
        gate_list = available_gate_strategy(inst)
        available_gate_dict[inst] = gate_list

    return available_gate_dict
