import math
from typing import Union

import pandas as pd


def get_data(filename) -> dict:
    data = pd.read_csv(filename)
    data = data.to_dict(orient="list")
    for i in range(len(data["data"])):
        if data["arrivee"][i] == "ZBTJ":
            data["callsign"][i] = data["callsign"][i] + " ar"
        else:
            data["callsign"][i] = data["callsign"][i] + " de"
    return data


def get_time_type(data: dict, data_index: int, data_type: str, quarter: Union[int, float]) -> str:
    """
    从当前 quarter 后一个小时这个时间节点开始， 之前的使用target time 之后的使用actual time
    """
    if math.isnan(quarter) and data_type == "de":
        return "ATOT"
    if math.isnan(quarter) and data_type == "ar":
        return "ALDT"

    if math.isinf(quarter) and data_type == "de":
        return "TTOT"
    if math.isinf(quarter) and data_type == "ar":
        return "TLDT"

    h = 60 * 60
    q = 60 * 15

    if data_type == "de":
        if (data['ATOT'][data_index] <= quarter * q + h) or (data['TTOT'][data_index] <= quarter * q + h):
            return "ATOT"
        return "TTOT"

    if (data['ALDT'][data_index] <= quarter * q + h) or (data['TLDT'][data_index] <= quarter * q + h):
        return "ALDT"
    return "TLDT"


def get_right_time(data: dict, data_index: int, data_type: str, quarter: Union[int, float]):
    """
    直接获取数据 减少心智负担
    """
    return data[get_time_type(data, data_index, data_type, quarter)][data_index]
