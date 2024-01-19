import os
import re

from FlightIncrease.IncreaseFlight import IncreaseFlight
from FlightIncrease.OutPut import OutPut
from FlightIncrease.Splice import concatenate_files_with_same_number
from GetInterval import GetInterval

if __name__ == "__main__":
    folder_path = "../results/gate_5_taxi_15"

    rate = 1  # the proportion of increased flights
    for filename in os.listdir(folder_path):
        match_process = re.search(r"process", filename, re.M | re.I)
        match_pn = re.search(r"PN", filename, re.M | re.I)
        if match_pn is None and filename.endswith(".csv") and match_process is None:
            filename = os.path.join(folder_path, filename)
            original_list = GetInterval(filename).interval
            increase_list = IncreaseFlight(original_list, rate).increase_flight()
            OutPut(increase_list, filename, rate)
            print(filename, "has been processed.")

    # 文件拼接
    folder_path1 = "../results/gate_5_taxi_15/"
    folder_path2 = "../results/IncreaseFlight_airline_rate_" + str(rate) + "/"
    output_path = "../results/ConcatenatedFiles_airline_rate_" + str(rate) + "/"

    concatenate_files_with_same_number(folder_path1, folder_path2, output_path)
