from FlightIncrease.IntervalType import IntervalBase


def delay_time(add_list: list, exist_interval: list) -> list:
    if len(add_list) == 0:
        return []

    if len(add_list) == 1:
        inst_type = add_list[0].begin_callsign[-2:].rstrip()

        if (add_list[0].begin_callsign == add_list[0].end_callsign) and (inst_type == "de"):
            return add_list

        # consider turbulence

        return ...

    for al in add_list:
        inst_type = al.begin_callsign[-2:].rstrip()
        if inst_type == "de":
            continue

        # consider turbulence

    return add_list


def consider_wake_turbulence(inst: IntervalBase, exist_interval: list):
    return ...
