import os
import re

from FlightIncrease.IncreaseFlight import IncreaseFlight
from FlightIncrease.OutPut import OutPut

if __name__ == "__main__":
    folder_path = "../data/results/gate_5_taxi_15"
    # folder_path = './data/error-in-data/buffer'

    for filename in os.listdir(folder_path):
        match_process = re.search(r"process", filename, re.M | re.I)
        match_pn = re.search(r"PN", filename, re.M | re.I)
        if match_pn is None and filename.endswith(".csv") and match_process is None:
            filename = os.path.join(folder_path, filename)
            increase_list = IncreaseFlight(filename).increase_list
            OutPut(increase_list, filename)

