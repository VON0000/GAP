import math
import os

import pandas as pd

from GateAllocation.GenernateSolution import generante_solution
from GateAllocation.optimization import find_numbers
from GateAllocation.outputdata import get_name
from dataReprocess.calculate_average_taxi_time import get_taxi_time
from dataReprocess.calculate_process_taxiing_time import clear_data


class Optimizer:
    def __init__(self, file_name):
        self.filename = file_name

    def optimize(self):
        _, _, obj = generante_solution(self.filename, 3, 0, 100, 3, 5)
        return obj


def get_file_path(file_name):
    sheetname = find_numbers(file_name)
    name = get_name(3, sheetname)
    file_path = ''.join(['../results/Traffic_GAP_test/', name, '_process.csv'])
    return file_path


def get_qfu_file_path(file_name):
    sheetname = find_numbers(file_name)
    name = get_name(3, sheetname)
    qfu_file_path = ''.join(['../results/Traffic_GAP_test/', name, '.csv'])
    return qfu_file_path


class Verify:
    def __init__(self, file_name):
        self.file_path = get_file_path(file_name)
        self.qfu_file_path = get_qfu_file_path(file_name)
        self.taxi_time = get_taxi_time()

    def verify(self):
        data = pd.read_csv(self.file_path)
        data = data.to_dict(orient="list")

        data_qfu = pd.read_csv(self.qfu_file_path)
        data_qfu = data_qfu.to_dict(orient="list")

        taxi_time_list = calculate_value(data, self.taxi_time, "PN_MANEX", data_qfu, "Parking")

        return sum(taxi_time_list)


def calculate_value(data: dict, taxi_time: dict, switch: str, data_qfu: dict, key: str):
    taxi_time_list = []
    counter = 0
    for i in range(len(data["data"])):
        gate = clear_data(data[key][i])
        if gate == "":
            continue
        if math.isnan(data_qfu["Parking"][i]):
            continue

        if data["arrivee"][i] == "ZBTJ" and data_qfu["QFU"][i] == "16L":
            taxi_time_list.append(taxi_time[switch][gate]["ARR-16L"])
        if data["arrivee"][i] == "ZBTJ" and data_qfu["QFU"][i] == "16R":
            taxi_time_list.append(taxi_time[switch][gate]["ARR-16R"])
        if data["arrivee"][i] != "ZBTJ":
            taxi_time_list.append(taxi_time[switch][gate]["DEP-16R"])

        counter += 1

    return taxi_time_list


def output(file_name_list: list, object_list: list, taxi_time_list: list):
    with open('result_compare.txt', 'w') as file:
        for i in range(len(file_name_list)):
            file.write(f"{file_name_list[i]}: {object_list[i]}, {taxi_time_list[i]} \n")


if __name__ == "__main__":
    folder_path = "../data/error-in-data"

    file_name_list = []
    object_list = []
    taxi_time_list = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file = os.path.join(folder_path, filename)
            optimizer = Optimizer(file)
            objective = optimizer.optimize()

            verify = Verify(file)
            taxi_time = verify.verify()

            print(f"{filename}: {objective}, {taxi_time}")

            file_name_list.append(filename)
            object_list.append(objective)
            taxi_time_list.append(taxi_time)

    output(file_name_list, object_list, taxi_time_list)
