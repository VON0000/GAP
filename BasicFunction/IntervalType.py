import abc
from typing import List, Union

from BasicFunction.GetData import get_time_type

HOUR = 60 * 60
MINUTE = 60


class IntervalBase(metaclass=abc.ABCMeta):
    def __init__(self, info_list: list):
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


def _longtime_arrivee(data: dict, index_list: list, quarter: Union[int, float]) -> tuple:
    begin_interval = data[get_time_type(data, index_list[0], "ar", quarter)][index_list[0]] + 5 * MINUTE
    end_interval = data[get_time_type(data, index_list[0], "ar", quarter)][index_list[0]] + 20 * MINUTE
    interval = end_interval - begin_interval
    return interval, begin_interval, end_interval


def _longtime_departure(data: dict, index_list: list, quarter: Union[int, float]) -> tuple:
    begin_interval = data[get_time_type(data, index_list[0], "de", quarter)][index_list[0]] - 20 * MINUTE
    end_interval = data[get_time_type(data, index_list[0], "de", quarter)][index_list[0]] - 5 * MINUTE
    interval = end_interval - begin_interval
    return interval, begin_interval, end_interval


def _shorttime(data: dict, index_list: list, quarter: Union[int, float]) -> tuple:
    begin_interval = data[get_time_type(data, index_list[0], "ar", quarter)][index_list[0]] + 5 * MINUTE
    end_interval = data[get_time_type(data, index_list[1], "de", quarter)][index_list[1]] - 5 * MINUTE
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


class IntervalType(IntervalBase):
    def __init__(self, interval_type: str, data: dict, index_list: List[int], quarter: Union[int, float]):
        info_list = _get_info_list(interval_type, data, index_list, quarter)
        super().__init__(info_list)
