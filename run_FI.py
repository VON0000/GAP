import os
import re

from BasicFunction.GetData import get_data
from BasicFunction.GetInterval import GetInterval
from FlightIncrease.IncreaseFlight import IncreaseFlight
from FlightIncrease.OutPut import OutPutFI
from FlightIncrease.Splice import concatenate_files_with_same_number
from GateAllocation.GateAllocation import GateAllocation
from GateAllocation.OutPutGAP import OutPutGAP

if __name__ == "__main__":

    rate = 0.4  # the proportion of increased flights

    folder_path = "./results/re_Traffic_GAP_2Pistes"

    folder_path3 = "./results/intermediateFile/re_optimization_" + str(rate) + "/"
    folder_path2 = "./results/intermediateFile/re_increase_" + str(rate) + "/"
    output_path = "./results/intermediateFile/re_concatenated_" + str(rate) + "/"

    for filename in os.listdir(folder_path):
        match_process = re.search(r"process", filename, re.M | re.I)
        match_pn = re.search(r"PN", filename, re.M | re.I)
        if match_pn is None and filename.endswith(".csv") and match_process is None:
            filename = os.path.join(folder_path, filename)
            data = get_data(filename)
            init_result = GateAllocation(data, 0, "MANEX").optimization(sans_taxiing_time=False)
            OutPutGAP(data, filename, folder_path3, "MANEX").output_final(init_result)

    for filename in os.listdir(folder_path3):
        if filename.endswith(".csv"):
            filename = os.path.join(folder_path3, filename)
            data = get_data(filename)
            original_list = GetInterval(data, 0, 0).interval
            increase_list = IncreaseFlight(original_list, rate).increase_flight()
            OutPutFI(increase_list, filename, folder_path2)
            print(filename, "has been processed.")

    # 文件拼接

    concatenate_files_with_same_number(folder_path3, folder_path2, output_path)
