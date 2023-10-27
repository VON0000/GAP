from typing import List

HOUR = 60 * 60
MINUTE = 60


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


class IntervalType:
    def __init__(self, interval_type: str, data: dict, index_list: List[int]):
        interval_info = None
        if interval_type == "longtime_arrivee":
            interval_info = _longtime_arrivee(data, index_list)
        if interval_type == "longtime_departure":
            interval_info = _longtime_departure(data, index_list)
        if interval_type == "shorttime":
            interval_info = _shorttime(data, index_list)

        self.interval = interval_info[0]
        self.begin_interval = interval_info[1]
        self.end_interval = interval_info[2]
        self.airline = data["Airline"][index_list[0]]
        self.registration = data["registration"][index_list[0]]
        self.begin_callsign = data["callsign"][index_list[0]]
        self.end_callsign = data["callsign"][index_list[-1]]
        self.wingspan = data["Wingspan"][index_list[0]]
        self.gate = data["Parking"][index_list[0]]
