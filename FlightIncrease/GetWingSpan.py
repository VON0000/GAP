import pandas as pd


class GetWingSpan:
    def __init__(self):
        self.gatesize = self.get_gate_size()

    @staticmethod
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
