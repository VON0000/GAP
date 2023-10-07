import copy
import os
import re

import numpy as np

import getdata
from getinterval import GetInterval


class GetIntervalForTest:
    def __init__(self, filename):
        self.data = self.get_data(filename)
        self.interval = self.presolve()
        self.gate_choose = self.get_gate_choose()

    @staticmethod
    def get_data(filename) -> dict:
        data = getdata.load_traffic(filename)
        return data

    def presolve(self) -> dict:
        data = self.data
        interval_inst = GetInterval()
        interval_data = interval_inst.presolve(96, data, 28, 5)
        interval = interval_data[0]
        return interval

    def get_gate_choose(self) -> list:
        gate_choose = []
        for i in range(len(self.interval["registration"])):
            if self.interval["begin_callsign"][i] == self.interval["end_callsign"][i]:
                callsign = self.get_callsign(self.interval["begin_callsign"][i])
                zbtj_type = self.get_zbtj_type(self.interval["begin_callsign"][i])
                registration = self.interval["registration"][i]
                for j in range(len(self.data["callsign"])):
                    if (
                        self.get_callsign(self.data["callsign"][j]) == callsign
                        and self.data["registration"][j] == registration
                    ):
                        if (
                            zbtj_type == "ar" and self.data["arrivee"][j] == "ZBTJ"
                        ) or (
                            zbtj_type == "de" and self.data["departure"][j] == "ZBTJ"
                        ):
                            gate_choose.append(self.data["Parking"][j])
            else:
                callsign1 = self.get_callsign(self.interval["begin_callsign"][i])
                zbtj_type1 = self.get_zbtj_type(self.interval["begin_callsign"][i])
                callsign2 = self.get_callsign(self.interval["end_callsign"][i])
                zbtj_type2 = self.get_zbtj_type(self.interval["end_callsign"][i])
                registration = self.interval["registration"][i]
                gate1 = ""
                gate2 = ""
                for j in range(len(self.data["callsign"])):
                    if (
                        self.get_callsign(self.data["callsign"][j]) == callsign1
                        and self.data["registration"][j] == registration
                    ):
                        if (
                            zbtj_type1 == "ar" and self.data["arrivee"][j] == "ZBTJ"
                        ) or (
                            zbtj_type1 == "de" and self.data["departure"][j] == "ZBTJ"
                        ):
                            gate1 = self.data["Parking"][j]
                    elif (
                        self.get_callsign(self.data["callsign"][j]) == callsign2
                        and self.data["registration"][j] == registration
                    ):
                        if (
                            zbtj_type2 == "ar" and self.data["arrivee"][j] == "ZBTJ"
                        ) or (
                            zbtj_type2 == "de" and self.data["departure"][j] == "ZBTJ"
                        ):
                            gate2 = self.data["Parking"][j]
                assert gate1 == gate2 or gate2 == "", "gate1 != gate2"
                gate_choose.append(gate1)
        return gate_choose

    @staticmethod
    def get_callsign(callsign) -> str:
        front_part = callsign[:-2]
        front_part = front_part.rstrip()
        return front_part

    @staticmethod
    def get_zbtj_type(callsign) -> str:
        zbtj_type = callsign[-2:]
        return zbtj_type


class Check:
    def __init__(self, interval, gate_choose):
        self.result: bool = self.check(interval, gate_choose)

    @staticmethod
    def get_obstruction(interval) -> list:
        n = len(interval["begin_interval"])
        obstruction = []
        fa = copy.deepcopy(interval["begin_interval"])
        fd = copy.deepcopy(interval["end_interval"])
        fa = np.array(fa)
        fd = np.array(fd)
        for i in range(n):
            part1 = np.where(
                (fa[i] <= fd) & (fd <= fd[i]) | (fa[i] <= fa) & (fa <= fd[i])
            )[0]
            part3 = np.where((fa <= fa[i]) & (fd[i] <= fd))[0]
            obs_list = np.union1d(part1, part3)
            obs_list = list(obs_list)
            obs_list.remove(i)
            obstruction.append(obs_list)
        return obstruction

    def check(self, interval, gate_choose) -> bool:
        obstruction = self.get_obstruction(interval)
        for i in range(len(obstruction)):
            for j in obstruction[i]:
                if gate_choose[i] == gate_choose[j]:
                    self.result = False
                    print(
                        interval["begin_callsign"][i],
                        interval["registration"][i],
                        interval["begin_callsign"][j],
                        interval["registration"][j],
                    )
                    return self.result
        self.result = True
        return self.result


class MainHandler:
    def __init__(self, filename: str):
        self.filename = filename
        self.interval = GetIntervalForTest(filename).interval
        self.gate_choose = GetIntervalForTest(filename).gate_choose
        self.check = Check(self.interval, self.gate_choose)
        self.result = self.check.check(self.interval, self.gate_choose)


if __name__ == "__main__":
    folder_path = "../results/gate_5_taxi_15"

    counter = 0
    # Iterate through the files in the folder
    for filename in os.listdir(folder_path):
        match = re.search(r"process", filename, re.M | re.I)
        if match is None and filename.endswith(".csv"):
            filename = os.path.join(folder_path, filename)
            main = MainHandler(filename)
            print(str(main.result), counter)
            counter += 1
