from FlightIncrease.IntervalType import IntervalType


class IncreaseFlight:
    def __init__(self, interval: list):
        self.interval = interval
        ...

    def find_size(self, inst: IntervalType) -> list:
        """
        根据当前interval实例的wingspan，找到合适的停机坪
        """
        ...

    def find_conflict(self, gate: str) -> bool:
        """
        检查当前停机坪是否有与添加interval冲突的interval
        """
        ...

    def find_suitable_gate(self, inst: IntervalType, gatesize: dict) -> IntervalType:
        """
        找到一个能停靠的停机坪
        """
        for i in range(len(gatesize["size_limit"])):
            if inst.wingspan <= gatesize["size_limit"][i]:
                if not self.find_conflict(gatesize["gate"][i]):
                    inst.gate = gatesize["gate"][i]
                    return inst
        ...

    def increase_flight(self, gatesize: dict) -> list:
        """
        通过循环尝试将停靠间隔塞进去
        :return: interval list 能增加的停靠间隔
        """
        increase_list = []
        for inst in self.interval:
            self.find_suitable_gate(inst, gatesize)

        return increase_list
