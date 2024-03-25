import os
import re

import pandas as pd

from dataReprocess.calculate import get_info


def run():
    taxi_time = get_taxi_time()

    folder_path = "../results"

    all_answer = []
    all_pn_answer = []

    for folder_name in os.listdir(folder_path):
        if folder_name == "intermediateFile":
            continue

        all_files = []
        all_pn_files = []
        for filename in os.listdir(folder_path + "/" + folder_name):
            filename = os.path.join(folder_path + "/" + folder_name, filename)
            match_pn = re.search(r"PN", filename, re.M | re.I)
            match_process = re.search(r"process", filename, re.M | re.I)
            if filename.endswith(".csv") and match_pn is None and match_process is None:
                switch = "MANEX"
                one_file_average = calculate_one_file(filename, taxi_time, switch)
                all_files.append(one_file_average)
            if filename.endswith(".csv") and match_pn is not None and match_process is None:
                switch = "PN_MANEX"
                one_file_average = calculate_one_file(filename, taxi_time, switch)
                all_pn_files.append(one_file_average)

        all_files_average = round(sum(all_files) / len(all_files))
        all_pn_files_average = round(sum(all_pn_files) / len(all_pn_files))

        info = get_info(folder_name)

        print(info + ["Norm", all_files_average])
        print(info + ["P<>N", all_pn_files_average])

        all_answer.append(info + ["Norm", all_files_average])
        all_pn_answer.append(info + ["P<>N", all_pn_files_average])

    out_put(all_answer + all_pn_answer)


def out_put(result: list):
    with open('result_average.txt', 'w') as file:
        file.write("Traffic;GAP;Runways;Airport;Mean\n")
        for r in result:
            r_list = [str(item) for item in r] + ["\n"]
            combined_ma_str = ";".join(r_list)
            file.write(combined_ma_str)


def calculate_one_file(filename: str, taxi_time: dict, switch: str):
    data = pd.read_csv(filename)
    data = data.to_dict(orient="list")

    taxi_time_list = []
    for i in range(len(data["data"])):
        if data["arrivee"][i] == "ZBTJ" and data["QFU"][i] == "16L":
            taxi_time_list.append(taxi_time[switch][str(data["Parking"][i])]["ARR-16L"])
        if data["arrivee"][i] == "ZBTJ" and data["QFU"][i] == "16R":
            taxi_time_list.append(taxi_time[switch][str(data["Parking"][i])]["ARR-16R"])
        if data["arrivee"][i] != "ZBTJ":
            taxi_time_list.append(taxi_time[switch][str(data["Parking"][i])]["DEP-16R"])

    return sum(taxi_time_list) / len(taxi_time_list)


def get_taxi_time():
    get_time_path = "../data/mintaxitime.xlsx"

    taxi_time_data = pd.read_excel(get_time_path, sheet_name="sheet1", header=2)
    taxi_time_data = taxi_time_data.to_dict(orient="list")
    real_taxi_time = {
        "MANEX": get_detail(taxi_time_data, "MANEX"),
        "MIN": get_detail(taxi_time_data, "MIN"),
        "PN_MANEX": get_detail(taxi_time_data, "PN_MANEX"),
        "PN_MIN": get_detail(taxi_time_data, "PN_MIN")
    }

    return real_taxi_time


def get_detail(taxi_time_data: dict, name: str) -> dict:
    if name == "MANEX":
        taxi_time = {}
        for i in range(len(taxi_time_data["Gate"])):
            taxi_time[str(taxi_time_data["Gate"][i])] = {
                "DEP-16R": int(taxi_time_data["DEP-16R"][i]),
                "ARR-16L": int(taxi_time_data["ARR-16L"][i]),
                "ARR-16R": int(taxi_time_data["ARR-16R"][i])
            }
        return taxi_time
    if name == "MIN":
        taxi_time = {}
        for i in range(len(taxi_time_data["Gate"])):
            taxi_time[str(taxi_time_data["Gate"][i])] = {
                "DEP-16R": int(taxi_time_data["DEP-16R.1"][i]),
                "ARR-16L": int(taxi_time_data["ARR-16L.1"][i]),
                "ARR-16R": int(taxi_time_data["ARR-16R.1"][i])
            }
        return taxi_time
    if name == "PN_MANEX":
        taxi_time = {}
        for i in range(len(taxi_time_data["Gate"])):
            taxi_time[str(taxi_time_data["Gate"][i])] = {
                "DEP-16R": int(taxi_time_data["DEP-16R.2"][i]),
                "ARR-16L": int(taxi_time_data["ARR-16L.2"][i]),
                "ARR-16R": int(taxi_time_data["ARR-16R.2"][i])
            }
        return taxi_time
    if name == "PN_MIN":
        taxi_time = {}
        for i in range(len(taxi_time_data["Gate"])):
            taxi_time[str(taxi_time_data["Gate"][i])] = {
                "DEP-16R": int(taxi_time_data["DEP-16R.3"][i]),
                "ARR-16L": int(taxi_time_data["ARR-16L.3"][i]),
                "ARR-16R": int(taxi_time_data["ARR-16R.3"][i])
            }
        return taxi_time


if __name__ == "__main__":
    run()
