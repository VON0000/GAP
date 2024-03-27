import math
import os
import re

import pandas as pd

from dataReprocess.calculate_average_taxi_time import get_taxi_time


def run():
    taxi_time = get_taxi_time()

    folder_path = "../results/"

    result = {}

    for folder_name in os.listdir(folder_path):
        if folder_name == "intermediateFile":
            continue

        match_augmente = re.search(r"augmente", folder_name, re.M | re.I)
        if match_augmente is not None:
            continue

        if folder_name == "Traffic_GAP_test":
            continue

        for filename in os.listdir(folder_path + "/" + folder_name):
            filename = os.path.join(folder_path + "/" + folder_name, filename)
            match_process = re.search(r"process", filename, re.M | re.I)
            match_pn = re.search(r"PN", filename, re.M | re.I)
            if filename.endswith(".csv") and match_process is not None and match_pn is None:
                calculate_one_file(filename, taxi_time, "MANEX", result)
            if filename.endswith(".csv") and match_process is not None and match_pn is not None:
                calculate_one_file(filename, taxi_time, "PN_MANEX", result)

    out_put(result)


def out_put(result: dict):
    result = pd.DataFrame(result)
    result.to_csv("result_min_or_not.csv", index=False)


def calculate_one_file(filename: str, taxi_time: dict, switch: str, result_dict: dict):
    data = pd.read_csv(filename)
    data = data.to_dict(orient="list")

    filename_qfu = filename.replace("_process", "")
    data_qfu = pd.read_csv(filename_qfu)
    data_qfu = data_qfu.to_dict(orient="list")
    qfu = data_qfu["QFU"]

    taxi_time_list = []
    for key in data:
        match_parking = re.search(r"parking", key, re.M | re.I)
        if match_parking is not None:
            taxi_time_list.append(taxi_time_list_average(calculate_value(data, taxi_time, switch, qfu, key)))

    result_dict[filename] = [round(i - taxi_time_list[0]) for i in taxi_time_list]

    return result_dict


def calculate_value(data: dict, taxi_time: dict, switch: str, qfu: list, key: str):
    taxi_time_list = []
    for i in range(len(data["data"])):
        gate = clear_data(data[key][i])
        if gate == "":
            continue
        if data["arrivee"][i] == "ZBTJ" and qfu[i] == "16L":
            taxi_time_list.append(taxi_time[switch][gate]["ARR-16L"])
        if data["arrivee"][i] == "ZBTJ" and qfu[i] == "16R":
            taxi_time_list.append(taxi_time[switch][gate]["ARR-16R"])
        if data["arrivee"][i] != "ZBTJ":
            taxi_time_list.append(taxi_time[switch][gate]["DEP-16R"])

    return taxi_time_list


def taxi_time_list_average(taxi_time_list: list):
    return sum(taxi_time_list) / len(taxi_time_list)


def clear_data(gate):
    if isinstance(gate, float):
        if math.isnan(gate):
            return ""
        return str(int(gate))
    elif isinstance(gate, int):
        # 直接转换为字符串
        return str(gate)
    elif isinstance(gate, str):
        if gate.endswith(".0"):
            # 去掉尾部的".0"
            return gate[:-2]
        return gate


if __name__ == "__main__":
    run()
