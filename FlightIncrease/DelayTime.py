from typing import List

import loguru

from BasicFunction.IntervalType import IntervalBase
from FlightIncrease.AircraftModel import AircraftModel


@loguru.logger.catch()
def delay_time(add_list: list, exist_interval: list, time_dict_type: str) -> list:
    """
    只考虑降落航班之间的尾流间隔
    | 1st acft → | A. L | A. M | A. H |
    |------------|------|------|------|
    |   A. L    | 60   | 120  | 180  |
    |   A. M    | 60   | 60   | 90   |
    |   A. H    | 60   | 60   | 90   |
    """
    useful_interval = [instance for instance in exist_interval if instance.begin_callsign[-2:].rstrip() == "ar"]

    if len(add_list) == 0:
        return []

    if len(add_list) == 1:
        inst_type = add_list[0].begin_callsign[-2:].rstrip()

        if (add_list[0].begin_callsign == add_list[0].end_callsign) and (inst_type == "de"):
            return add_list

        find_insertion_location(useful_interval, add_list[0], time_dict_type)

        return add_list

    for al in add_list:
        inst_type = al.begin_callsign[-2:].rstrip()
        if inst_type == "de":
            continue

        find_insertion_location(useful_interval, al, time_dict_type)

    return add_list


def find_insertion_location(useful_interval: List[IntervalBase], inst: IntervalBase,
                            time_dict_type: str) -> IntervalBase:
    """
    事实上，先按照在这个instance之前的interval更新，后按照在这个instance之后的interval更新，不会产生错误。更新的时间一定是按照最晚的来的。
    In fact, updating according to the interval before this instance and then updating according to the interval after
    this instance will not produce an error. The update time is always based on the latest.

    输出为更改时间后（加入尾流）的interval
    """
    before_inst_list = [instance for instance in useful_interval if instance.begin_interval <= inst.begin_interval]
    before_conflict = False
    for bi in before_inst_list:
        wake_turbulence = get_wake_turbulence(bi, inst)
        # 增加的航班降落时间加上尾流间隔 与前一个航班冲突
        if bi.begin_interval <= inst.begin_interval < bi.begin_interval + wake_turbulence:
            # 更新interval 推迟尾流间隔的时间
            inst.begin_interval = bi.begin_interval + wake_turbulence
            before_conflict = True

    after_inst_list = [instance for instance in useful_interval if instance.begin_interval > inst.begin_interval]
    after_conflict = False
    for ai in after_inst_list:
        wake_turbulence = get_wake_turbulence(inst, ai)
        # 增加的航班降落时间加上尾流间隔 与后一个航班冲突
        if inst.begin_interval <= ai.begin_interval < inst.begin_interval + wake_turbulence:
            # 更新interval 推迟尾流间隔的时间
            wake_turbulence = get_wake_turbulence(ai, inst)
            inst.begin_interval = ai.begin_interval + wake_turbulence
            after_conflict = True

    # 使用递归的原因: 对于一个interval来讲，先按顺序推到最晚的没有冲突的时间，此时时间对于整个list来讲不一定在什么位置，
    # 于是再次循环，检查与list前面部分是否有冲突。
    if after_conflict or before_conflict:
        return find_insertion_location(useful_interval, inst, time_dict_type)

    delta_time = inst.begin_interval - inst.time_dict["ar"][time_dict_type] - 5 * 60
    inst.end_interval = inst.end_interval + delta_time
    return inst


def get_wake_turbulence(front_inst: IntervalBase, end_inst: IntervalBase) -> int:
    """
    | 1st acft → | A. L | A. M | A. H |
    |------------|------|------|------|
    |   A. L    | 60   | 120  | 180  |
    |   A. M    | 60   | 60   | 90   |
    |   A. H    | 60   | 60   | 90   |
    """
    if AircraftModel(front_inst.aircraft_model).aircraft_type == "L":
        return 60
    if AircraftModel(front_inst.aircraft_model).aircraft_type == "M":
        if AircraftModel(end_inst.aircraft_model).aircraft_type == "L":
            return 120
        return 60
    if AircraftModel(front_inst.aircraft_model).aircraft_type == "H":
        if AircraftModel(end_inst.aircraft_model).aircraft_type == "L":
            return 180
        return 90
