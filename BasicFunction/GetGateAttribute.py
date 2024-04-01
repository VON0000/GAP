import re

import pandas as pd


def get_gate_size() -> dict:
    """
    从“E:/pycharm/GAP/data/wingsizelimit.xls”获取每个停机坪的大小
    """
    data = pd.read_excel("./data/wingsizelimit.xls", sheet_name=None)
    sheet_data = data["sheet1"]
    gatesize = sheet_data.to_dict(orient="list")

    key_to_convert = "gate"

    if key_to_convert in gatesize:
        gatesize[key_to_convert] = [str(item) for item in gatesize[key_to_convert]]

    return gatesize


def get_dependent_gate(gate_size: dict) -> dict:
    dependent_gate_dict = {}
    for g in gate_size["gate"]:
        if not (("L" in g) or ("R" in g)):
            # g = 414 时， re.findall(r"\d+", g) = ['414']， 因此 ref_g = 414R 414L 414 会被选中
            # g = 601 时， re.findall(r"\d+", g) = ['601']， 因此 ref_g = 601 会被选中g
            dependent_gate_dict[g] = [ref_g for ref_g in gate_size["gate"] if
                                      re.findall(r"\d+", g) == re.findall(r"\d+", ref_g)]
        else:
            # g = 414L 时， re.findall(r"\d+", g) = ['414']， 因此 ref_g = 414L 414 会被选中
            dependent_gate_dict[g] = [ref_g for ref_g in gate_size["gate"] if
                                      (re.findall(r"\d+", g) == [ref_g] or g == ref_g)]

    return dependent_gate_dict


class GetGateAttribute:
    gate_size = get_gate_size()
    dependent_gate_dict = get_dependent_gate(gate_size)

    def __init__(self, gate: str):
        self.gate = gate
        self.size = self.get_wing_size()
        self.dependent_gate = self.get_dependent_gate()

    def get_wing_size(self) -> float:
        index = GetGateAttribute.gate_size["gate"].index(self.gate)
        return GetGateAttribute.gate_size["size_limit"][index]

    def get_dependent_gate(self) -> list:
        return GetGateAttribute.dependent_gate_dict[self.gate]
