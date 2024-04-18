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


def re_optimization():
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


if __name__ == "__main__":

    rate = 0.5  # the proportion of increased flights

    folder_path = "./results/re_Traffic_GAP_2Pistes"

    folder_path4 = "./results/intermediateFile/t_a_total/re_optimization_actual_3_" + str(rate) + "/"
    folder_path3 = "./results/intermediateFile/t_a_total/re_optimization_target_3_" + str(rate) + "/"
    folder_path2 = "./results/intermediateFile/t_a_total/re_increase_3_" + str(rate) + "/"
    output_path = "./results/intermediateFile/t_a_total/re_concatenated_3_" + str(rate) + "/"

    # re_optimization()

    for filename in os.listdir(folder_path3):
        if filename.endswith(".csv"):
            filename_target = os.path.join(folder_path3, filename)
            data_target = get_data(filename_target)
            target_list = GetInterval(data_target, 0, 0).interval

            filename_actual = os.path.join(folder_path4, filename.split("\\")[-1])
            data_actual = get_data(filename_actual)
            actual_list = GetInterval(data_actual, math.nan, 0).interval

            increase_list = IncreaseFlight(actual_list, rate).increase_flight(target_list)
            OutPutFI(increase_list, filename_target, folder_path2)
            print(filename, "has been processed.")

    # 文件拼接

    concatenate_files_with_same_number(folder_path4, folder_path2, output_path)
