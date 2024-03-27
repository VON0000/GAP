import math
from typing import Union

import numpy as np
import pandas as pd

from BasicFunction.GetTimeType import get_time_type
from BasicFunction.IntervalType import IntervalType

HOUR = 60 * 60
MINUTE = 60


def get_data(filename) -> dict:
    data = pd.read_csv(filename)
    data = data.to_dict(orient="list")
    for i in range(len(data["data"])):
        if data["arrivee"][i] == "ZBTJ":
            data["callsign"][i] = data["callsign"][i] + " ar"
        else:
            data["callsign"][i] = data["callsign"][i] + " de"
    return data


class GetInterval:
    def __init__(self, filename: str, quarter: Union[int, float]):
        self.data = get_data(filename)
        self.interval = self.get_interval(quarter)

    def _get_interval_one(self, registration: str, quarter: Union[int, float]) -> list:
        """
        计算当前registration的停靠间隔
        """
        interval = []
        flight_list = self._flight_list_sorted(registration, quarter)
        i = 0

        if self.data["departure"][flight_list[0]] == "ZBTJ":
            interval_instance = IntervalType(
                "longtime_departure", self.data, [flight_list[i]], quarter
            )
            interval.append(interval_instance)
            i = i + 1

        while i < len(flight_list):
            if i + 1 >= len(flight_list):
                interval_instance = IntervalType(
                    "longtime_arrivee", self.data, [flight_list[i]], quarter
                )
                interval.append(interval_instance)
                break
            interval_time = (
                    self.data[get_time_type(self.data, flight_list[i + 1], "de", quarter)][flight_list[i + 1]]
                    - self.data[get_time_type(self.data, flight_list[i], "ar", quarter)][flight_list[i]]
            )
            if interval_time <= HOUR:
                interval_instance = IntervalType(
                    "shorttime", self.data, [flight_list[i], flight_list[i + 1]], quarter
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
                    "longtime_arrivee", self.data, [flight_list[i]], quarter
                )
                interval.append(interval_instance)
                interval_instance = IntervalType(
                    "longtime_departure", self.data, [flight_list[i + 1]], quarter
                )
                interval.append(interval_instance)
            i = i + 2
        return interval

    def _flight_list_sorted(self, registration: str, quarter: Union[int, float]) -> list:
        """
        对flight_list进行排序
        """
        flight_list = np.where(np.array(self.data["registration"]) == registration)[0]
        time_list = []
        for i in flight_list:
            if self.data["departure"][i] == "ZBTJ":
                time_list.append(self.data[get_time_type(self.data, i, "de", quarter)][i])
            else:
                time_list.append(self.data[get_time_type(self.data, i, "ar", quarter)][i])
        enumerated_list = list(enumerate(time_list))
        sorted_list = sorted(enumerated_list, key=lambda x: x[1])
        sorted_indices = [x[0] for x in sorted_list]

        sorted_flight_list = sorted_indices + flight_list[0]
        return sorted_flight_list

    def get_interval(self, quarter: Union[int, float]) -> list:
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
                interval.extend(self._get_interval_one(i, quarter))
        for u in interval:
            if u.end_callsign[-2:] == "de":
                u.end_interval = u.end_interval + 5 * MINUTE
        return interval

    def transform_second_to_half_minute(self):
        for i in self.interval:
            i.begin_interval = math.ceil(i.begin_interval / (MINUTE / 2))
            i.end_interval = math.ceil(i.end_interval / (MINUTE / 2))
            i.interval = math.ceil(i.interval / (MINUTE / 2))
        return self.interval
