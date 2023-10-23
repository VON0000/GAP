import pandas as pd


class GetInterval:
    def __init__(self, filename: str):
        self.data = self.get_data(filename)

    @staticmethod
    def get_data(filename) -> dict:
        data = pd.read_csv(filename)
        data = data.to_dict(orient="list")
        n = len(data["data"])
        for i in range(n):
            if data["arrivee"][i] == "ZBTJ":
                data["callsign"][i] = data["callsign"][i] + " ar"
            else:
                data["callsign"][i] = data["callsign"][i] + " de"
        return data

    def get_interval(self) -> dict:
        ...


