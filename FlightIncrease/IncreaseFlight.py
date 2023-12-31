import copy
import random
import re
from typing import Union

from FlightIncrease.AirlineType import AirlineType, get_group_dict
from FlightIncrease.GetInterval import GetInterval
from FlightIncrease.GetWingSpan import GetWingSpan
from FlightIncrease.IntervalType import IntervalBase


def _is_overlapping(time1, time2) -> bool:
    """
    判断两个时间段是否有重叠
    False 为没有冲突
    True 为有冲突
    """
    if time1[0] <= time2[0] <= time1[1]:
        return True
    if time2[0] <= time1[0] <= time2[1]:
        return True
    return False


def _conflict_half(
        aug_inst: IntervalBase, inst: IntervalBase, gate: str, flag: bool
) -> bool:
    """
    False 为没有冲突
    True 为有冲突
    """
    if inst.gate == gate or inst.gate == re.findall(r"\d+", gate):
        flag = _is_overlapping(
            (inst.begin_interval, inst.end_interval),
            (aug_inst.begin_interval, aug_inst.end_interval),
        )
    return flag


def _conflict_all(
        aug_inst: IntervalBase, inst: IntervalBase, gate: str, flag: bool
) -> bool:
    """
    False 为没有冲突
    True 为有冲突
    """
    if re.findall(r"\d+", inst.gate) == re.findall(r"\d+", gate):
        flag = _is_overlapping(
            (inst.begin_interval, inst.end_interval),
            (aug_inst.begin_interval, aug_inst.end_interval),
        )
    return flag


class IncreaseFlight:
    def __init__(self, filename: str, rate: float = 1):
        inst_interval = GetInterval(filename)
        inst_wingspan = GetWingSpan()
        self.rate = rate
        self.interval = inst_interval.interval
        self.gatesize = inst_wingspan.gatesize
        self.increase_list = self.increase_flight()

    def find_conflict(self, aug_inst: IntervalBase, gate: str) -> bool:
        """
        检查当前停机坪是否有与添加interval冲突的interval
        False 为没有冲突
        True 为有冲突
        """
        flag = False
        counter = 0
        while not flag and counter < len(self.interval):
            inst = self.interval[counter]
            # 414
            if not (("L" in gate) or ("R" in gate)):
                flag = _conflict_all(aug_inst, inst, gate, flag)
            # 414L 414R
            else:
                flag = _conflict_half(aug_inst, inst, gate, flag)
            counter = counter + 1
        return flag

    def find_suitable_gate(self, inst: IntervalBase) -> Union[IntervalBase, None]:
        """
        找到一个能停靠的停机坪
        """
        available_gate = []
        gate = AirlineType(inst.airline).available_gate
        for g in gate:
            idx = self.gatesize["gate"].index(g)
            if inst.wingspan <= self.gatesize["size_limit"][idx]:
                if not self.find_conflict(inst, self.gatesize["gate"][idx]):
                    available_gate.append(g)
        if len(available_gate) == 0:
            return None
        else:
            inst.gate = random.choice(available_gate)
            return inst

    def increase_flight(self) -> list:
        """
        通过循环尝试将停靠间隔塞进去
        :return: interval list 能增加的停靠间隔
        """
        original_interval = copy.deepcopy(self.interval)
        n = len(self.interval)  # the number of original flights
        increase_list = []
        while len(increase_list) < n * self.rate:
            inst = random.choice(original_interval)
            idx = original_interval.index(inst)
            original_interval.remove(inst)
            new_inst = self.find_suitable_gate(inst)
            if new_inst is not None:
                if new_inst.end_callsign != new_inst.end_callsign:
                    increase_list.append(new_inst)
                    self.interval.append(new_inst)
                else:
                    new_inst_neighbor = self._get_neighbor_flight(idx, inst, original_interval)
                    if new_inst_neighbor is not None:
                        increase_list.append(new_inst)
                        self.interval.append(new_inst)
                        increase_list.append(new_inst_neighbor)
                        self.interval.append(new_inst_neighbor)
        return increase_list

    def _get_neighbor_flight(self, idx, inst, original_interval) -> Union[IntervalBase, None]:
        # find the inst before(de) or after(ar) the inst
        # if the inst and the inst_neighbor have the same registration, find another gate for the inst_neighbor
        inst_type = inst.begin_callsign[-2:].rstrip
        if inst_type == "ar":
            inst_neighbor = original_interval[idx]
        else:
            inst_neighbor = original_interval[idx - 1]
        if inst.registration == inst_neighbor.registration:
            new_inst_neighbor = self.find_suitable_gate(inst)
            if new_inst_neighbor is not None:
                return new_inst_neighbor
        return None

