import random
import re
from typing import Union

from FlightIncrease.GetInterval import GetInterval
from FlightIncrease.GetWingSpan import GetWingSpan
from FlightIncrease.IntervalType import IntervalType


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
    aug_inst: IntervalType, inst: IntervalType, gate: str, flag: bool
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
    aug_inst: IntervalType, inst: IntervalType, gate: str, flag: bool
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
    def __init__(self, filename: str):
        inst_interval = GetInterval(filename)
        inst_wingspan = GetWingSpan()
        self.interval = inst_interval.interval
        self.gatesize = inst_wingspan.gatesize
        self.increase_list = self.increase_flight()

    def find_conflict(self, aug_inst: IntervalType, gate: str) -> bool:
        """
        检查当前停机坪是否有与添加interval冲突的interval
        False 为没有冲突
        True 为有冲突
        """
        flag = False
        counter = 0
        while not flag:
            inst = self.interval[counter]
            # 414
            if not (re.search("L", gate) or re.search("R", gate)):
                flag = _conflict_all(aug_inst, inst, gate, flag)
            # 414L 414R
            else:
                flag = _conflict_half(aug_inst, inst, gate, flag)
            counter = counter + 1
        return flag

    def find_suitable_gate(self, inst: IntervalType) -> Union[IntervalType, None]:
        """
        找到一个能停靠的停机坪
        """
        available_gate = []
        for i in range(len(self.gatesize["size_limit"])):
            if inst.wingspan <= self.gatesize["size_limit"][i]:
                if not self.find_conflict(inst, self.gatesize["gate"][i]):
                    available_gate.append(self.gatesize["gate"][i])
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
        increase_list = []
        for inst in self.interval:
            new_inst = self.find_suitable_gate(inst)
            if new_inst is not None:
                increase_list.append(new_inst)
        return increase_list
