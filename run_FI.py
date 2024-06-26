import math
import os
import re

from BasicFunction.GetData import get_data
from BasicFunction.GetInterval import GetInterval
from FlightIncrease.IncreaseFlight import IncreaseFlight
from FlightIncrease.OutPut import OutPutFI
from FlightIncrease.Splice import concatenate_files_with_same_number
from GateAllocation.GateAllocation import GateAllocation
from GateAllocation.OutPutGAP import OutPutGAP


def re_optimization(folder_path4, folder_path3, folder_path):
    for filename in os.listdir(folder_path):
        match_process = re.search(r"process", filename, re.M | re.I)
        match_pn = re.search(r"PN", filename, re.M | re.I)
        if match_pn is None and filename.endswith(".csv") and match_process is None:
            filename = os.path.join(folder_path, filename)
            data = get_data(filename)
            target_result = GateAllocation(data, 0, "MANEX").optimization(sans_taxiing_time=False)
            OutPutGAP(data, filename, folder_path3, "MANEX").output_final(target_result)
            actual_result = GateAllocation(data, 0, "MANEX", math.nan).optimization(sans_taxiing_time=False)
            OutPutGAP(data, filename, folder_path4, "MANEX").output_final(actual_result)


def increase_concatenate_files_with_same_number(folder_path_target_opt: str, folder_path_actual_opt: str,
                                                folder_path_increase: str, output_path_concatenate: str, rate: float,
                                                seed: int):
    for filename in os.listdir(folder_path_target_opt):
        if filename.endswith(".csv"):
            filename_target = os.path.join(folder_path_target_opt, filename)
            data_target = get_data(filename_target)
            target_list = GetInterval(data_target, 0, 0).interval

            filename_actual = os.path.join(folder_path_actual_opt, filename.split("\\")[-1])
            data_actual = get_data(filename_actual)
            actual_list = GetInterval(data_actual, math.nan, 0).interval

            increase_list = IncreaseFlight(actual_list, rate).increase_flight(target_list, seed)
            OutPutFI(increase_list, filename_target, folder_path_increase)
            print(filename, "has been processed.")

    # 文件拼接

    concatenate_files_with_same_number(folder_path_actual_opt, folder_path_increase, output_path_concatenate)


if __name__ == "__main__":
    rate = 0.5  # the proportion of increased flights

    folder_path_origin = "./results/re_Traffic_GAP_2Pistes"

    folder_path_actual_opt = "./results/intermediateFile/re_optimization_actual/"
    folder_path_target_opt = "./results/intermediateFile/re_optimization_target/"
    folder_path_increase = "./results/intermediateFile/re_increase/"
    output_path_concatenate = "./results/intermediateFile/re_concatenated/"

    re_optimization(folder_path_actual_opt, folder_path_target_opt, folder_path_origin)
    increase_concatenate_files_with_same_number(folder_path_target_opt, folder_path_actual_opt, folder_path_increase,
                                                output_path_concatenate, rate, 0)
