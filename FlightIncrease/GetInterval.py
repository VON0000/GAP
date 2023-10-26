import numpy as np
import pandas as pd

from FlightIncrease.IntervalType import IntervalType

HOUR = 60 * 60
MINUTE = 60


class GetInterval:
    def __init__(self, filename: str):
        self.data = self.get_data(filename)
        self.interval = self.get_interval()

    @staticmethod
    def get_data(filename) -> dict:
        data = pd.read_csv(filename)
        data = data.to_dict(orient="list")
        for i in range(len(data["data"])):
            if data["arrivee"][i] == "ZBTJ":
                data["callsign"][i] = data["callsign"][i] + " ar"
            else:
                data["callsign"][i] = data["callsign"][i] + " de"
        return data

    def _get_interval_one(self, registration: str) -> list:
        """
        计算当前registration的停靠间隔
        """
        interval = []
        flight_list = self.flight_list_sorted(registration)
        i = 0

        if self.data["departure"][flight_list[0]] == "ZBTJ":
            interval_instance = IntervalType(
                "longtime_departure", self.data, [flight_list[i]]
            )
            interval.append(interval_instance)
            i = i + 1

        while i < len(flight_list):
            if i + 1 >= len(flight_list):
                interval_instance = IntervalType(
                    "longtime_arrivee", self.data, [flight_list[i]]
                )
                interval.append(interval_instance)
                break
            interval_time = (
                self.data["ATOT"][flight_list[i + 1]]
                - self.data["ALDT"][flight_list[i]]
            )
            if interval_time <= HOUR:
                interval_instance = IntervalType(
                    "shorttime", self.data, [flight_list[i], flight_list[i + 1]]
                )
                if interval_time >= HOUR * (5 + 5 + 15 + 15) / 60:
                    pass
                else:
                    interval_instance.interval = 30 * MINUTE
                    interval_instance.end_interval = (
                        interval_instance.begin_interval + interval_instance.interval
                    )
                interval.append(interval_instance)
            else:
                interval_instance = IntervalType(
                    "longtime_arrivee", self.data, [flight_list[i]]
                )
                interval.append(interval_instance)
                interval_instance = IntervalType(
                    "longtime_departure", self.data, [flight_list[i + 1]]
                )
                interval.append(interval_instance)
            i = i + 2
        return interval

    def flight_list_sorted(self, registration: str) -> list:
        """
        对flight_list进行排序
        """
        flight_list = np.where(np.array(self.data["registration"]) == registration)[0]
        time_list = []
        for i in flight_list:
            if self.data["departure"][i] == "ZBTJ":
                time_list.append(self.data["ATOT"][i])
            else:
                time_list.append(self.data["ALDT"][i])

        enumerated_list = list(enumerate(time_list))
        sorted_list = sorted(enumerated_list, key=lambda x: x[1])
        sorted_indices = [x[0] for x in sorted_list]

        sorted_flight_list = sorted_indices + flight_list[0]
        return sorted_flight_list

    def get_interval(self) -> list:
        """
        使用data中的数据，计算每个航班的停靠间隔
        首先选出同属于一个飞机执飞的航班，然后计算这些航班之间的停靠间隔
        保存形式为类的列表，每个类中包含一个停靠间隔的信息
        :return: interval
        """
        interval = []
        sample = ""
        for i in self.data["registration"]:
            if i == sample:
                continue
            else:
                sample = i
                interval.extend(self._get_interval_one(i))
        return interval


class GetWingSpan:
    def __init__(self):
        self.gatesize = self.get_gate_size()

    @staticmethod
    def get_gate_size() -> dict:
        """
        从“E:/pycharm/GAP/data/wingsizelimit.xls”获取每个停机坪的大小
        """
        data = pd.read_excel("./data/wingsizelimit.xls", sheet_name=None)
        sheet_data = data["sheet1"]
        gatesize = sheet_data.to_dict(orient="list")
        return gatesize


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


def output():
    """
    将结果输出到csv文件中
    """
    ...
