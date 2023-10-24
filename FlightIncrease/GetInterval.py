from typing import List

import numpy as np
import pandas as pd

HOUR = 60 * 60
MINUTE = 60


class IntervalType:
    def __init__(self, interval_type: str, data: dict, index_list: List[int]):
        interval_info = None
        if interval_type == "longtime_arrivee":
            interval_info = self.longtime_arrivee(data, index_list)
        if interval_type == "longtime_departure":
            interval_info = self.longtime_departure(data, index_list)
        if interval_type == "shorttime":
            interval_info = self.shorttime(data, index_list)

        self.interval = interval_info[0]
        self.begin_interval = interval_info[1]
        self.end_interval = interval_info[2]
        self.airline = data["airline"][index_list[0]]
        self.registration = data["registration"][index_list[0]]
        self.begin_callsign = data["callsign"][index_list[0]]
        self.end_callsign = data["callsign"][index_list[-1]]
        self.wingspan = data["wingspan"][index_list[0]]

    @staticmethod
    def longtime_arrivee(data: dict, index_list: list):
        begin_interval = data["ALDT"][index_list[0]] + 5 * MINUTE
        end_interval = data["ALDT"][index_list[0]] + 20 * MINUTE
        interval = end_interval - begin_interval
        return interval, begin_interval, end_interval

    @staticmethod
    def longtime_departure(data: dict, index_list: list):
        begin_interval = data["ATOT"][index_list[0]] - 20 * MINUTE
        end_interval = data["ATOT"][index_list[0]] - 5 * MINUTE
        interval = end_interval - begin_interval
        return interval, begin_interval, end_interval

    @staticmethod
    def shorttime(data: dict, index_list: list):
        begin_interval = data["ALDT"][index_list[0]] + 5 * MINUTE
        end_interval = data["ATOT"][index_list[1]] - 5 * MINUTE
        interval = end_interval - begin_interval
        return interval, begin_interval, end_interval


class GetInterval:
    def __init__(self, filename: str):
        self.data = self.get_data(filename)

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

    def get_interval_one(self, registration: str) -> list:
        """
        计算当前registration的停靠间隔
        """
        interval = []
        flight_list = self.flight_list_sorted(registration)
        i = 0

        while i < len(flight_list):
            if self.data["departure"][flight_list[i]] == "ZBTJ":
                interval_instance = IntervalType(
                    "longtime_departure", self.data, [flight_list[i]]
                )
                i = i + 1
            else:
                if i + 1 < len(flight_list):
                    ...
                    if interval_time <= HOUR:
                        ...
                        if interval_time >= HOUR * (5 + 5 + 15 + 15) / 60:
                            pass
                        else:
                            ...
                    else:
                        ...
                else:
                    ...
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

        sorted_flight_list = sorted_list + flight_list[0]
        return sorted_flight_list

    def get_interval(self) -> list:
        """
        使用data中的数据，计算每个航班的停靠间隔
        首先选出同属于一个飞机执飞的航班，然后计算这些航班之间的停靠间隔
        保存形式为类的列表，每个类中包含一个航班的信息
        :return: interval
        """
        interval = []
        sample = ""
        for i in self.data["registration"]:
            if i == sample:
                break
            else:
                sample = i
                interval.append(self.get_interval_one(i))
            ...
        return interval

    def increase_flight(self) -> list:
        """
        通过循环尝试将停靠间隔塞进去
        """
        ...

    def output(self):
        """
        将结果输出到csv文件中
        """
        ...
