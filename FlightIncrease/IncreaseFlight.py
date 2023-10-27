import random
import re
from typing import Union

from FlightIncrease.GetInterval import GetInterval
from FlightIncrease.GetWingSpan import GetWingSpan
from FlightIncrease.IntervalType import IntervalType


class IncreaseFlight:
    def __init__(self, filename: str):
        inst_interval = GetInterval(filename)
        inst_wingspan = GetWingSpan()
        self.interval = inst_interval.interval
        self.gatesize = inst_wingspan.gatesize
        ...

    def find_size(self, inst: IntervalType) -> list:
        """
        根据当前interval实例的wingspan，找到合适的停机坪
        """
        ...

    def conflict_half(self, inst: IntervalType, gate: str, flag: bool) -> bool:
        if inst.gate == gate or inst.gate == re.findall(r"\d+", gate):
            ...
        return flag

    def conflict_all(self, inst: IntervalType, gate: str, flag: bool) -> bool:
        if re.findall(r"\d+", inst.gate) == re.findall(r"\d+", gate):
            ...
        return flag

    def find_conflict(self, gate: str) -> bool:
        """
        检查当前停机坪是否有与添加interval冲突的interval
        """
        flag = False
        counter = 0
        while not flag:
            inst = self.interval[counter]
            # 414
            if not (re.search("L", gate) or re.search("R", gate)):
                flag = self.conflict_all(inst, gate, flag)
            # 414L 414R
            else:
                flag = self.conflict_half(inst, gate, flag)
            counter = counter + 1
        return flag

    def find_suitable_gate(self, inst: IntervalType) -> Union[IntervalType, None]:
        """
        找到一个能停靠的停机坪
        """
        available_gate = []
        for i in range(len(self.gatesize["size_limit"])):
            if inst.wingspan <= self.gatesize["size_limit"][i]:
                if not self.find_conflict(self.gatesize["gate"][i]):
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
            if self.find_suitable_gate(inst):
                increase_list.append(inst)
        return increase_list
