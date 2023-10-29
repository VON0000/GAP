import os
import re

from FlightIncrease.IncreaseFlight import IncreaseFlight
from FlightIncrease.OutPut import OutPut

if __name__ == "__main__":
    folder_path = "../data/error-in-data"
    # folder_path = './data/error-in-data/buffer'

    for filename in os.listdir(folder_path):
        match = re.search(r"process", filename, re.M | re.I)
        if match is None and filename.endswith(".csv"):
            filename = os.path.join(folder_path, filename)
            increase_list = IncreaseFlight(filename).increase_list
            OutPut(increase_list, filename)

