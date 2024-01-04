import copy
import random
import re
import sys
from typing import Union

import loguru

from FlightIncrease.AirlineType import AirlineType
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
                # add the neighbor flight(if available) and the new inst
                add_list = self._get_neighbor_flight(new_inst, idx, original_interval)
                increase_list.extend(add_list)
                self.interval.extend(add_list)
        return increase_list

    @loguru.logger.catch
    def _get_neighbor_flight(self, new_inst: IntervalBase, idx: int, original_interval: list) -> list:
        if new_inst.begin_callsign != new_inst.end_callsign:
            return [new_inst]

        # find another inst before(de) or after(ar) the inst
        # if the inst and the inst_neighbor have the same registration, find another gate for the inst_neighbor
        inst_type = new_inst.begin_callsign[-2:].rstrip()

        # the first flight of instances is departure
        if inst_type == "de" and idx == 0:
            return [new_inst]

        # the last flight of instances is arrival
        if inst_type == "ar" and idx == len(original_interval):
            return [new_inst]

        inst_neighbor = original_interval[idx - 1] if inst_type == "de" else original_interval[idx]

        # the inst is at the beginning or the end of the group, it has no neighbor
        if new_inst.registration != inst_neighbor.registration:
            return [new_inst]

        inst_neighbor_type = inst_neighbor.begin_callsign[-2:].rstrip()
        # Dealing with extreme scenarios:
        # before this iteration, the inst in the middle has already been deleted, like(de ar de) => (de de)
        # In this iteration, one of the "de" has been chosen.
        # We deleted it and remain the other one.
        if inst_neighbor_type == inst_type:
            return []

        # the inst is in the middle of the group, it has a neighbor
        new_inst_neighbor = self.find_suitable_gate(inst_neighbor)
        original_interval.remove(inst_neighbor)

        # the inst_neighbor has no suitable gate
        if new_inst_neighbor is None:
            return []

        # the inst_neighbor has a suitable gate
        return [new_inst, new_inst_neighbor]
