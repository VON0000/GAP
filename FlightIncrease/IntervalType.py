import abc
from typing import List

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
        self.gate = str(info_list[8])


def _longtime_arrivee(data: dict, index_list: list):
    begin_interval = data["ALDT"][index_list[0]] + 5 * MINUTE
    end_interval = data["ALDT"][index_list[0]] + 20 * MINUTE
    interval = end_interval - begin_interval
    return interval, begin_interval, end_interval


def _longtime_departure(data: dict, index_list: list):
    begin_interval = data["ATOT"][index_list[0]] - 20 * MINUTE
    end_interval = data["ATOT"][index_list[0]] - 5 * MINUTE
    interval = end_interval - begin_interval
    return interval, begin_interval, end_interval


def _shorttime(data: dict, index_list: list):
    begin_interval = data["ALDT"][index_list[0]] + 5 * MINUTE
    end_interval = data["ATOT"][index_list[1]] - 5 * MINUTE
    interval = end_interval - begin_interval
    return interval, begin_interval, end_interval


def _get_info_list(interval_type: str, data: dict, index_list: List[int]):
    interval_info = None
    if interval_type == "longtime_arrivee":
        interval_info = _longtime_arrivee(data, index_list)
    if interval_type == "longtime_departure":
        interval_info = _longtime_departure(data, index_list)
    if interval_type == "shorttime":
        interval_info = _shorttime(data, index_list)

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
    ]
    return info_list


class IntervalType(IntervalBase):
    def __init__(self, interval_type: str, data: dict, index_list: List[int]):
        info_list = _get_info_list(interval_type, data, index_list)
        super().__init__(info_list)

