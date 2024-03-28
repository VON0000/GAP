import math
import os
import re

from BasicFunction.GetData import get_data
from FlightIncrease.IncreaseFlight import IncreaseFlight
from FlightIncrease.OutPut import OutPut
from FlightIncrease.Splice import concatenate_files_with_same_number
from BasicFunction.GetInterval import GetInterval

if __name__ == "__main__":

    rate = 0.5  # the proportion of increased flights

    folder_path = "../results/Traffic_GAP_2Pistes"

    folder_path2 = "../results/Traffic_IncreaseFlight_GAP_2Pistes_" + str(rate) + "/"
    output_path = "../results/Traffic_ConcatenatedFiles_GAP_2Pistes_" + str(rate) + "/"

    for filename in os.listdir(folder_path):
        match_process = re.search(r"process", filename, re.M | re.I)
        match_pn = re.search(r"PN", filename, re.M | re.I)
        if match_pn is None and filename.endswith(".csv") and match_process is None:
            filename = os.path.join(folder_path, filename)
            data = get_data(filename)
            original_list = GetInterval(data, math.nan, 28).interval
            increase_list = IncreaseFlight(original_list, rate).increase_flight()
            OutPut(increase_list, filename, folder_path2)
            print(filename, "has been processed.")

    # 文件拼接

    concatenate_files_with_same_number(folder_path, folder_path2, output_path)
