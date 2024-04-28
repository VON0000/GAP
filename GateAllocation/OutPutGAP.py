import os
import re
from copy import deepcopy
from typing import Union

import pandas as pd

from BasicFunction.AirlineType import AirlineType
from BasicFunction.GetNumberInFilename import find_numbers
from BasicFunction.IntervalType import IntervalBase


class OutPutGAP:
    def __init__(self, data: dict, filename: str, out_path: str, pattern: str):
        self.data = deepcopy(data)
        self.out_path = out_path
        self.filename = filename
        self.pattern = pattern
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
        del self.data["Parking"]

        change_times = 0
        for rl_idx in range(len(result_list)):
            for i in range(len(self.data["callsign"])):
                self._update_data_process(i, rl_idx, result_list[rl_idx])
            if rl_idx > 0:
                change_times += get_change_times(result_list[rl_idx - 1], result_list[rl_idx])
        self.data["change_times"] = change_times

        remote_numbers = get_remote_numbers(result_list[0], result_list[-1])
        self.data["remote_numbers"] = remote_numbers

        name = find_numbers(re.search(r'[\\/][^\\/]*$', self.filename).group()) + ["_process"] + ["_"]
        out_name = [self.out_path] + name + [self.pattern] + [".csv"]
        output_file_path = "".join(out_name)

        data = pd.DataFrame(self.data)
        data.to_csv(output_file_path, index=False)

    def output_final(self, result: dict):
        for i in range(len(self.data["data"])):
            self._update_data_final(i, result)

        name = find_numbers(re.search(r'[\\/][^\\/]*$', self.filename).group()) + ["_"]
        out_name = [self.out_path] + name + [self.pattern] + [".csv"]
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

    def _get_interval(self, index: int, result: dict) -> Union[IntervalBase, None]:
        """
        获取每个 data 对应的 interval
        根据 registration 和 callsign
        """
        inst_lst = [inst for inst in self._get_interval_list(result) if
                    inst.registration == self.data["registration"][index] and (self.data["callsign"][index] in [
                        inst.begin_callsign, inst.end_callsign])]

        assert inst_lst is not None, "这条数据没有对应的实例" + self.data["registration"][index] + \
                                     self.data["callsign"][index]
        return inst_lst[0]


def create_directory(path):
    try:
        # 如果文件夹不存在，则创建它
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directory '{path}' was created.")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_change_times(init_result: dict, last_result: dict) -> int:
    """
    给定任意一个 inst 根据他的 registration 和 callsign 找到在 last_result.keys() 中对应的实例
    根据该实例对应的 gate 并计算 init_result[inst] 与 gate 不同的数量
    """
    counter = 0
    for inst in init_result:
        if inst.begin_callsign == inst.end_callsign:
            counter = _get_change_times_counter(inst, init_result, last_result, counter, inst.begin_callsign)
        else:
            counter = _get_change_times_counter(inst, init_result, last_result, counter, inst.begin_callsign)
            counter = _get_change_times_counter(inst, init_result, last_result, counter, inst.end_callsign)
    return counter


def _get_possible_ref(inst: IntervalBase, last_result: dict, call_sign: str) -> list:
    possible_ref = [ref for ref in last_result.keys() if ref.registration == inst.registration and (
            ref.begin_callsign == call_sign or ref.end_callsign == call_sign)]
    return possible_ref


def _get_change_times_counter(inst: IntervalBase, init_result: dict, last_result: dict, counter: int,
                              call_sign: str) -> int:
    possible_ref = _get_possible_ref(inst, last_result, call_sign)
    if possible_ref:
        ref = possible_ref[0]
        if init_result[inst] != last_result[ref]:
            counter += 1
    return counter


def get_remote_numbers(init_result: dict, last_result: dict) -> int:
    """
    给定任意一个 inst 如果他的 airline 属于 domestic
    则判断他的 airline 对应的 available_gate 是否有 这个 inst 在 last_result 中的 gate
    """
    counter = 0
    for inst in init_result:
        if inst.begin_callsign == inst.end_callsign:
            counter = _get_remote_counter(inst, last_result, counter, inst.begin_callsign)
        else:
            counter = _get_remote_counter(inst, last_result, counter, inst.begin_callsign)
            counter = _get_remote_counter(inst, last_result, counter, inst.end_callsign)
        return counter


def _get_remote_counter(inst: IntervalBase, last_result: dict, counter: int, call_sign: str) -> int:
    if AirlineType(inst.airline).group_dict["domestic"]:
        possible_ref = _get_possible_ref(inst, last_result, call_sign)
        if possible_ref:
            ref = possible_ref[0]
            if last_result[ref] not in AirlineType(inst.airline).airline_gate:
                counter += 1
    return counter
