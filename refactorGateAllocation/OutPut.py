import os
import re
from copy import deepcopy
from typing import List

import pandas as pd

from BasicFunction.IntervalType import IntervalBase


class OutPut:
    def __init__(self, data: dict, filename: str, out_path: str):
        self.data = deepcopy(data)
        self.out_path = out_path
        self.filename = filename
        create_directory(out_path)

    def output_process(self, result_list: list):
        del self.data["data"]
        del self.data["TTOT"]
        del self.data["TLDT"]
        del self.data["ATOT"]
        del self.data["ALDT"]
        del self.data["Type"]
        del self.data["Wingspan"]
        del self.data["Airline"]
        del self.data["QFU"]

        for rl_idx in range(len(result_list)):
            for i in range(len(self.data["callsign"])):
                self._update_data_process(i, rl_idx, result_list[rl_idx])

        name = find_numbers(re.search(r'\\([^\\]+)$', self.filename).group(1)) + ["process"] + [".csv"]
        out_name = [self.out_path] + name
        output_file_path = "".join(out_name)

        data = pd.DataFrame(self.data)
        data.to_csv(output_file_path, index=False)

    def output_final(self, result: dict):
        for i in range(len(self.data["data"])):
            self._update_data_final(i, result)

        name = find_numbers(re.search(r'\\([^\\]+)$', self.filename).group(1)) + [".csv"]
        out_name = [self.out_path] + name
        output_file_path = "".join(out_name)

        data = pd.DataFrame(self.data)
        data.to_csv(output_file_path, index=False)

    @staticmethod
    def _get_interval_list(result: dict) -> list:
        return list(result.keys())

    def _update_data_final(self, index: int, result: dict):
        interval = self._get_interval(index, result)
        if self.data["callsign"][index] == interval.begin_callsign:
            self.data["QFU"][index] = interval.begin_qfu.split("-", 1)[1]
        else:
            self.data["QFU"][index] = interval.end_qfu.split("-", 1)[1]
        self.data["callsign"][index] = self.data["callsign"][index].split(" ")[0]
        self.data["Parking"][index] = result[interval]

    def _update_data_process(self, index: int, lst_index: int, result: dict):
        interval = self._get_interval(index, result)
        if "Parking" + str(lst_index) not in self.data:
            self.data["Parking" + str(lst_index)] = [""] * len(self.data["callsign"])
        self.data["Parking" + str(lst_index)][index] = result[interval]

    def _get_interval(self, index: int, result: dict) -> IntervalBase:
        """
        获取每个 data 对应的 interval
        根据 registration 和 callsign
        """
        inst_begin = [inst for inst in self._get_interval_list(result) if
                      inst.registration == self.data["registration"][index] and inst.begin_callsign ==
                      self.data["callsign"][index]]

        inst_end = [inst for inst in self._get_interval_list(result) if
                    inst.registration == self.data["registration"][index] and inst.end_callsign ==
                    self.data["callsign"][index]]

        if inst_begin == inst_end:
            return inst_begin[0]

        return (inst_begin + inst_end)[0]


def create_directory(path):
    try:
        # 如果文件夹不存在，则创建它
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directory '{path}' was created.")
    except Exception as e:
        print(f"An error occurred: {e}")


def find_numbers(text: str) -> List[str]:
    numbers = re.findall(r"\d+", text)
    return numbers
