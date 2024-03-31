import pandas as pd


def get_gate_size() -> dict:
    """
    从“E:/pycharm/GAP/data/wingsizelimit.xls”获取每个停机坪的大小
    """
    data = pd.read_excel("../data/wingsizelimit.xls", sheet_name=None)
    sheet_data = data["sheet1"]
    gatesize = sheet_data.to_dict(orient="list")

    key_to_convert = "gate"

    if key_to_convert in gatesize:
        gatesize[key_to_convert] = [str(item) for item in gatesize[key_to_convert]]

    return gatesize


class GetWingSpan:
    gate_size = get_gate_size()

    def __init__(self, gate: str):
        self.gate = gate
        self.size = self.get_wing_size()

    def get_wing_size(self) -> float:
        index = GetWingSpan.gate_size["gate"].index(self.gate)
        return GetWingSpan.gate_size["size_limit"][index]
