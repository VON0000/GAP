import abc
from typing import List, Union

from BasicFunction.GetData import get_right_time

HOUR = 60 * 60
MINUTE = 60


class IntervalBase(metaclass=abc.ABCMeta):
    def __init__(self, info_list: list):
        qfu_info_list = info_list[11:]

        self.interval = info_list[0]
        self.begin_interval = info_list[1]
        self.end_interval = info_list[2]
        self.airline = info_list[3]
        self.registration = info_list[4]
        self.begin_callsign = info_list[5]
        self.end_callsign = info_list[6]
        self.wingspan = info_list[7]
        self.gate = (
            str(info_list[8]).split(".")[0]
            if str(info_list[8]).endswith(".0")
            else str(info_list[8])
        )
        self.aircraft_model = info_list[9]
        self.time_dict = info_list[10]
        self.begin_qfu = qfu_info_list[0]
        self.end_qfu = qfu_info_list[-1]


def _longtime_arrivee(data: dict, index_list: list, quarter: Union[int, float]) -> tuple:
    begin_interval = get_right_time(data, index_list[0], "ar", quarter) + 5 * MINUTE
    end_interval = get_right_time(data, index_list[0], "ar", quarter) + 20 * MINUTE
    interval = end_interval - begin_interval
    return interval, begin_interval, end_interval


def _longtime_departure(data: dict, index_list: list, quarter: Union[int, float]) -> tuple:
    begin_interval = get_right_time(data, index_list[0], "de", quarter) - 20 * MINUTE
    end_interval = get_right_time(data, index_list[0], "de", quarter) - 5 * MINUTE
    interval = end_interval - begin_interval
    return interval, begin_interval, end_interval


def _shorttime(data: dict, index_list: list, quarter: Union[int, float]) -> tuple:
    begin_interval = get_right_time(data, index_list[0], "ar", quarter) + 5 * MINUTE
    end_interval = get_right_time(data, index_list[1], "de", quarter) - 5 * MINUTE
    interval = end_interval - begin_interval
    return interval, begin_interval, end_interval


def _get_info_list(interval_type: str, data: dict, index_list: List[int], quarter: Union[int, float]) -> list:
    interval_info = None
    time_dict = {"ar": {"TTOT": 0, "TLDT": 0, "ATOT": 0, "ALDT": 0},
                 "de": {"TTOT": 0, "TLDT": 0, "ATOT": 0, "ALDT": 0}}
    if interval_type == "longtime_arrivee":
        interval_info = _longtime_arrivee(data, index_list, quarter)
        time_dict = {"ar": {"TTOT": data["TTOT"][index_list[0]], "TLDT": data["TLDT"][index_list[0]],
                            "ATOT": data["ATOT"][index_list[0]], "ALDT": data["ALDT"][index_list[0]]}, "de": {}}
    if interval_type == "longtime_departure":
        interval_info = _longtime_departure(data, index_list, quarter)
        time_dict = {"de": {"TTOT": data["TTOT"][index_list[0]], "TLDT": data["TLDT"][index_list[0]],
                            "ATOT": data["ATOT"][index_list[0]], "ALDT": data["ALDT"][index_list[0]]}, "ar": {}}
    if interval_type == "shorttime":
        interval_info = _shorttime(data, index_list, quarter)
        time_dict = {"ar": {"TTOT": data["TTOT"][index_list[0]], "TLDT": data["TLDT"][index_list[0]],
                            "ATOT": data["ATOT"][index_list[0]], "ALDT": data["ALDT"][index_list[0]]},
                     "de": {"TTOT": data["TTOT"][index_list[1]], "TLDT": data["TLDT"][index_list[1]],
                            "ATOT": data["ATOT"][index_list[1]], "ALDT": data["ALDT"][index_list[1]]}}

    info_list = [
        interval_info[0],
        interval_info[1],
        interval_info[2],
        data["Airline"][index_list[0]],
        data["registration"][index_list[0]],
        data["callsign"][index_list[0]],
        data["callsign"][index_list[-1]],
        data["Wingspan"][index_list[0]],
        data["Parking"][index_list[0]],
        data["Type"][index_list[0]],
        time_dict,
    ]
    return info_list


def _get_qfu_info(data: dict, index_list: List[int], quarter: Union[int, float], time_tide: dict) -> list:
    h = 60 * 60

    qfu_info_list = []
    for i in index_list:
        if data["callsign"][i].split(maxsplit=1)[1] == "de":
            qfu_info_list.append("DEP-16R")
            return qfu_info_list

        time = get_right_time(data, i, "ar", quarter)

        time = time // h

        if time >= 23:
            time = 23

        if time <= 0:
            time = 0

        if time_tide[time]:
            qfu_info_list.append("ARR-16L")
        else:
            qfu_info_list.append("ARR-16R")

    return qfu_info_list


class IntervalType(IntervalBase):
    def __init__(self, interval_type: str, data: dict, index_list: List[int], quarter: Union[int, float],
                 time_tide: dict):
        info_list = _get_info_list(interval_type, data, index_list, quarter)
        qfu_info_list = _get_qfu_info(data, index_list, quarter, time_tide)
        super().__init__(info_list + qfu_info_list)
