from typing import List

from FlightIncrease.IntervalType import IntervalBase
from FlightIncrease.AircraftModel import AircraftModel


def delay_time(add_list: list, exist_interval: list) -> list:
    useful_interval = [instance for instance in exist_interval if instance.begin_callsign[-2:].rstrip() == "ar"]

    if len(add_list) == 0:
        return []

    if len(add_list) == 1:
        inst_type = add_list[0].begin_callsign[-2:].rstrip()

        if (add_list[0].begin_callsign == add_list[0].end_callsign) and (inst_type == "de"):
            return add_list

        find_insertion_location(useful_interval, inst=add_list[0])

        return add_list

    for al in add_list:
        inst_type = al.begin_callsign[-2:].rstrip()
        if inst_type == "de":
            continue

        find_insertion_location(useful_interval, inst=al)

    return add_list


def find_insertion_location(useful_interval: List[IntervalBase], inst: IntervalBase) -> IntervalBase:
    """
    事实上，先按照在这个instance之前的interval更新，后按照在这个instance之后的interval更新，不会产生错误。更新的时间一定是按照最晚的来的。
    In fact, updating according to the interval before this instance and then updating according to the interval after
    this instance will not produce an error. The update time is always based on the latest.
    """
    before_inst_list = [instance for instance in useful_interval if instance.begin_interval <= inst.begin_interval]
    before_conflict = False
    for bi in before_inst_list:
        wake_turbulence = get_wake_turbulence(bi, inst)
        if bi.begin_interval <= inst.begin_interval < bi.begin_interval + wake_turbulence:
            # update the delay time of the instance
            inst.begin_interval = bi.begin_interval + wake_turbulence
            before_conflict = True

    after_inst_list = [instance for instance in useful_interval if instance.begin_interval > inst.begin_interval]
    after_conflict = False
    for ai in after_inst_list:
        wake_turbulence = get_wake_turbulence(inst, ai)
        if inst.begin_interval <= ai.begin_interval < inst.begin_interval + wake_turbulence:
            # update the delay time of the instance
            wake_turbulence = get_wake_turbulence(ai, inst)
            inst.begin_interval = ai.begin_interval + wake_turbulence
            after_conflict = True

    if after_conflict or before_conflict:
        return find_insertion_location(useful_interval, inst)

    return inst


def get_wake_turbulence(front_inst: IntervalBase, end_inst: IntervalBase):
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
