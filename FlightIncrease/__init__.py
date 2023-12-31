import os
import re

from FlightIncrease.IncreaseFlight import IncreaseFlight
from FlightIncrease.OutPut import OutPut
from FlightIncrease.Splice import concatenate_files_with_same_number

if __name__ == "__main__":
    folder_path = "../results/gate_5_taxi_15"

    rate = 0.5  # the proportion of increased flights
    for filename in os.listdir(folder_path):
        match_process = re.search(r"process", filename, re.M | re.I)
        match_pn = re.search(r"PN", filename, re.M | re.I)
        if match_pn is None and filename.endswith(".csv") and match_process is None:
            filename = os.path.join(folder_path, filename)
            increase_list = IncreaseFlight(filename, rate).increase_list
            OutPut(increase_list, filename, rate)

    # 文件拼接
    folder_path1 = "../results/gate_5_taxi_15/"
    folder_path2 = "../results/IncreaseFlight_airline/"
    output_path = "../results/ConcatenatedFiles_airline/"

    concatenate_files_with_same_number(folder_path1, folder_path2, output_path)
