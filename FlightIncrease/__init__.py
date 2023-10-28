import numpy as np
import pandas as pd


def build_data(data: dict) -> dict:
    ...
    return data


def output(interval_list: list, filename: str):
    """
    将结果输出到csv文件中
    """
    data = {
        "data": [],
        "callsign": [],
        "departure": [],
        "arrivee": [],
        "TTOT": [],
        "TLDT": [],
        "ATOT": [],
        "ALDT": [],
        "Type": [],
        "Wingspan": [],
        "Airline": [],
        "QFU": [],
        "Parking": [],
        "registration": [],
    }
    reference = pd.read_csv(filename)
    reference = reference.to_dict(orient="list")
    for i in interval_list:
        callsign = i.callsign[:-2].rstrip()
        poss_list = set(np.where(np.array(reference["callsign"]) == callsign)[0]) & set(
            np.where(np.array(reference["registration"]) == i.registration)[0]
        )
        assert poss_list != set()
        for p in poss_list:
            if callsign[-2:] == "de" and reference["departure"][p] == "ZBTJ":
                data = build_data(data)
            if callsign[-2:] == "ar" and reference["arrivee"][p] == "ZBTJ":
                data = build_data(data)
