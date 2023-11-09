import random
import re
from typing import List

import pandas as pd

from FlightIncrease.AirlineType import AirlineType
from FlightIncrease.IntervalType import IntervalBase


def _get_reference(filename: str) -> dict:
    reference = pd.read_csv(filename)
    reference = reference.to_dict(orient="list")
    return reference


def data_init() -> dict:
    data = {
        "data": [],
        "callsign": [],
        "departure": [],
        "arrivee": [],
        "TTOT": [],
        "TLDT": [],
        "ATOT": [],
        "ALDT": [],
        "Type": [],
        "Wingspan": [],
        "Airline": [],
        "QFU": [],
        "Parking": [],
        "registration": [],
    }
    return data


def _build_element(
    c: IntervalBase, data: dict, callsign_list: List[str], filename: str
) -> dict:
    for cl in callsign_list:
        data["data"].append("".join(find_numbers(filename)))
        data["callsign"].append("NEW" + cl[:-2].rstrip())

        if cl[-2:] == "de":
            data["departure"].append("ZBTJ")
            data["arrivee"].append("None")
            data["ATOT"].append(c.end_interval)
            data["ALDT"].append(random.randint(c.end_interval, 100000))
        else:
            data["departure"].append("None")
            data["arrivee"].append("ZBTJ")
            data["ATOT"].append(random.randint(0, c.begin_interval - 5 * 60))
            data["ALDT"].append(c.begin_interval - 5 * 60)

        data["TTOT"].append("None")
        data["TLDT"].append("None")

        data["Type"].append("None")
        data["Wingspan"].append(c.wingspan)
        data["Airline"].append(AirlineType(c.airline).type)
        data["QFU"].append("None")
        data["Parking"].append(c.gate)
        data["registration"].append("NEW" + c.registration)
    return data


def _build_data(increase_list: List[IntervalBase], filename: str) -> dict:
    data_dict = data_init()
    for c in increase_list:
        if c.begin_callsign != c.end_callsign:
            data_dict = _build_element(
                c, data_dict, [c.begin_callsign, c.end_callsign], filename
            )
        else:
            data_dict = _build_element(c, data_dict, [c.begin_callsign], filename)
    return data_dict


def find_numbers(text: str) -> List[str]:
    numbers = re.findall(r"\d+", text)
    return numbers


class OutPut:
    def __init__(self, increase_list: List[IntervalBase], filename: str):
        self.to_csv(increase_list, filename)

    @staticmethod
    def to_csv(increase_list: List[IntervalBase], filename: str):
        name = find_numbers(re.search(r'\\([^\\]+)$', filename).group(1)) + [".csv"]
        out_name = ["../results/IncreaseFlight_type/"] + name
        output_file_path = "".join(out_name)

        data = _build_data(increase_list, filename)
        data = pd.DataFrame(data)
        data.to_csv(output_file_path, index=False)
