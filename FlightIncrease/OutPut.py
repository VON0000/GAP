import os
import re
from typing import List

import pandas as pd

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
        "delay": [],
    }
    return data


def _build_element(
        c: IntervalBase, data: dict, callsign_list: List[str], filename: str
) -> dict:
    for cl in callsign_list:
        data["data"].append("".join(find_numbers(filename)))
        data["callsign"].append("NEW" + cl[:-2].rstrip())

        if cl[-2:] == "de":
            delta_time = 0
            data["departure"].append("ZBTJ")
            data["arrivee"].append("Default")

            data["ATOT"].append(c.end_interval)
            data["ALDT"].append(c.time_dict["de"]["ALDT"])

            data["TTOT"].append(c.time_dict["de"]["TTOT"])
            data["TLDT"].append(c.time_dict["de"]["TLDT"])
        else:
            data["departure"].append("Default")
            data["arrivee"].append("ZBTJ")

            delta_time = c.begin_interval - 5 * 60 - c.time_dict["ar"]["ALDT"]
            data["ATOT"].append(c.time_dict["ar"]["ATOT"] + delta_time)
            data["ALDT"].append(c.begin_interval - 5 * 60)

            data["TTOT"].append(c.time_dict["ar"]["TTOT"] + delta_time)
            data["TLDT"].append(c.time_dict["ar"]["TLDT"] + delta_time)

        data["Type"].append("Default")
        data["Wingspan"].append(c.wingspan)
        data["Airline"].append(c.airline)
        data["QFU"].append("Default")
        data["Parking"].append(c.gate)
        data["registration"].append("NEW" + c.registration)
        data["delay"].append(delta_time)
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
    def __init__(self, increase_list: List[IntervalBase], filename: str, rate: float = 1):
        increase_list_sorted_by_registration = sorted(increase_list, key=lambda inst: inst.registration)
        self.to_csv(increase_list_sorted_by_registration, filename, rate)

    def to_csv(self, increase_list: List[IntervalBase], filename: str, rate: float):
        name = find_numbers(re.search(r'\\([^\\]+)$', filename).group(1)) + [".csv"]
        out_path = "../results/IncreaseFlight_airline_with_delay_rate_" + str(rate) + "/"
        self.create_directory(out_path)
        out_name = [out_path] + name
        output_file_path = "".join(out_name)

        data = _build_data(increase_list, filename)
        data = pd.DataFrame(data)
        data.to_csv(output_file_path, index=False)

    @staticmethod
    def create_directory(path):
        try:
            # 如果文件夹不存在，则创建它
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"Directory '{path}' was created.")
        except Exception as e:
            print(f"An error occurred: {e}")
