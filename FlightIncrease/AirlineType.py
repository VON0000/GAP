import pandas as pd


def get_airline_info(name: str) -> dict:
    filename = "../data/group/FlightIncrease/" + name + ".xlsx"
    data = pd.read_excel(filename, sheet_name=None, header=None)
    df = data["Feuil1"].astype(str)
    airline_info = {row[0]: list(row[1:]) for _, row in df.iterrows()}
    for i in airline_info:
        airline_info[i] = [x.split('.')[0] if x.endswith('.0') else x for x in airline_info[i] if x != 'nan']
    return airline_info


class AirlineType:
    def __init__(self, airline: str):
        self.airline = airline
        self.type = self.get_type()
        self.available_gate = self.get_available_gate()

    @classmethod
    def get_airline_info(cls) -> tuple:
        cargo = get_airline_info("cargo")
        domestic = get_airline_info("domestic")
        international = get_airline_info("international")
        return cargo, domestic, international

    @classmethod
    def get_available_gate_info(cls) -> dict:
        all_available = get_airline_info("airlinesgate")
        return all_available

    def get_type(self) -> str:
        cargo, domestic, international = self.get_airline_info()
        if self.airline in cargo.keys():
            return "cargo"
        elif self.airline in domestic.keys():
            return "domestic"
        elif self.airline in international.keys():
            return "international"
        else:
            raise ValueError("AirlineType.get_type: airline not found")

    def get_available_gate(self) -> list:
        all_available = self.get_available_gate_info()
        if self.airline in all_available.keys():
            return all_available[self.airline]
        else:
            return []
