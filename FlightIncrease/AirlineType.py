import pandas as pd


def get_airline_info(name: str) -> dict:
    filename = "../data/group/FlightIncrease/" + name + ".xlsx"
    data = pd.read_excel(filename, sheet_name=None, header=None)
    df = data["Feuil1"]
    airline_info = {row[0]: list(row[1:]) for _, row in df.iterrows()}
    return airline_info


class AirlineType:
    def __init__(self, airline: str):
        self.airline = airline
        self.type = self.get_type()
        self.available_gate = self.get_available_gate()

    @classmethod
    def get_airline_info(cls, name: str) -> dict:
        ...

    def get_type(self) -> str:
        ...

    def get_available_gate(self) -> list:
        ...
