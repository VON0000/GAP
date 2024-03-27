import math
from typing import Union


def get_time_type(data: dict, data_index: int, data_type: str, quarter: Union[int, float]) -> str:
    """
    从当前 quarter 后一个小时这个时间节点开始， 之前的使用target time 之后的使用actual time
    """
    if math.isnan(quarter) and data_type == "de":
        return "ATOT"
    if math.isnan(quarter) and data_type == "ar":
        return "ALDT"

    h = 60 * 60
    q = 60 * 15

    if data_type == "de":
        if data['ATOT'][data_index] <= quarter * q + h or data['TTOT'][data_index] < quarter * q:
            return "ATOT"
        return "TTOT"

    if data['ALDT'][data_index] <= quarter * q + h or data['TLDT'][data_index] < quarter * q:
        return "ALDT"
    return "TLDT"
