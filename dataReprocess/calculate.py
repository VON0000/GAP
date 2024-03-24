import os
import re
import statistics

import pandas as pd


def run():
    folder_path = "./all_results"

    mtt_all = []
    ftt_all = []
    delay_all = []

    for folder_name in os.listdir(folder_path):
        info = get_info(folder_name)

        data = {}
        pn_data = {}
        for filename in os.listdir(folder_path + "/" + folder_name):
            filename = os.path.join(folder_path + "/" + folder_name, filename)
            match_pn = re.search(r"PN", filename, re.M | re.I)
            if match_pn is None and filename.endswith(".csv"):
                data = get_all_file(data, filename)
            if match_pn is not None and filename.endswith(".csv"):
                pn_data = get_all_file(pn_data, filename)

        mtt_answer = calculate_mtt_answer(data)
        mtt_pn_answer = calculate_mtt_answer(pn_data)
        ftt_answer = calculate_ftt_answer(data)
        ftt_pn_answer = calculate_ftt_answer(pn_data)
        delay_answer = calculate_delay_answer(data)
        delay_pn_answer = calculate_delay_answer(pn_data)

        mtt_result = info + ["Norm"] + mtt_answer
        mtt_pn_result = info + ["P<>N"] + mtt_pn_answer

        ftt_result = info + ["Norm"] + ftt_answer
        ftt_pn_result = info + ["P<>N"] + ftt_pn_answer

        delay_result = info + ["Norm"] + delay_answer
        delay_pn_result = info + ["P<>N"] + delay_pn_answer

        mtt_all.extend([mtt_result, mtt_pn_result])
        ftt_all.extend([ftt_result, ftt_pn_result])
        delay_all.extend([delay_result, delay_pn_result])

    output_data(mtt_all, ftt_all, delay_all)


def output_data(mtt_all, ftt_all, delay_all):
    with open('result.txt', 'w') as file:
        file.write("MinTaxiTime (sec.)\n")
        file.write("Traffic;GAP;Runways;Airport;Mean;StDev;Min;Max\n")
        for ma in mtt_all:
            ma_list = [str(item) for item in ma] + ["\n"]
            combined_ma_str = ";".join(ma_list)
            file.write(combined_ma_str)
        file.write("FinalTaxiTime (sec.)\n")
        file.write("Traffic;GAP;Runways;Airport;Mean;StDev;Min;Max\n")
        for fa in ftt_all:
            fa_list = [str(item) for item in fa] + ["\n"]
            combined_fa_str = ";".join(fa_list)
            file.write(combined_fa_str)
        file.write("Delay (sec.)\n")
        file.write("Traffic;GAP;Runways;Airport;Mean;StDev;Min;Max\n")
        for da in delay_all:
            da_list = [str(item) for item in da] + ["\n"]
            combined_da_str = ";".join(da_list)
            file.write(combined_da_str)


def calculate_delay_answer(data):
    request = []
    for key in data:
        for i in range(len(data[key]["RwyDelay"])):
            if data[key]["RwyDelay"][i] != "":
                request.append(data[key]["RwyDelay"][i] + data[key]["TaxiDelay"][i])

    mean = sum(request) / len(request)
    max_value = max(request)
    min_value = min(request)
    std_dev = statistics.stdev(request)

    return [round(mean), round(std_dev), round(min_value), round(max_value)]


def calculate_ftt_answer(data):
    request = []
    for key in data:
        request.extend(data[key]["FinalTaxiTime"])

    mean = sum(request) / len(request)
    max_value = max(request)
    min_value = min(request)
    std_dev = statistics.stdev(request)

    return [round(mean), round(std_dev), round(min_value), round(max_value)]


def calculate_mtt_answer(data):
    request = []
    for key in data:
        request.extend(data[key]["MinTaxiTime"])

    mean = sum(request) / len(request)
    max_value = max(request)
    min_value = min(request)
    std_dev = statistics.stdev(request)

    return [round(mean), round(std_dev), round(min_value), round(max_value)]


def get_all_file(data, filename):
    on_file = pd.read_csv(filename)
    on_file = on_file.to_dict(orient="list")

    error_key = list(on_file.keys())[0]
    keys = error_key.split(";")

    data_on_file = {}

    for v in on_file[error_key]:
        values = v.split(";")
        for i in range(len(keys)):

            if keys[i] not in data_on_file:
                data_on_file[keys[i]] = []

            if i < len(values):
                try:
                    data_on_file[keys[i]].append(int(values[i]))
                except ValueError:
                    data_on_file[keys[i]].append(values[i])
            else:
                data_on_file[keys[i]].append("")

    data[filename] = data_on_file

    return data


def get_info(folder_name):
    info = []
    if re.search(r"Augmente", folder_name, re.M | re.I):
        info.append("Incr")
    else:
        info.append("Curr")

    if re.search(r"Baseline", folder_name, re.M | re.I):
        info.append("Basic")
    else:
        info.append("MinTT")

    if re.search(r"mix", folder_name, re.M | re.I):
        info.append("mix")
    elif re.search(r"16R", folder_name, re.M | re.I):
        info.append("One")
    else:
        info.append("Both")

    assert len(info) == 3
    return info


if __name__ == "__main__":
    run()
