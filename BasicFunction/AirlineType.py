import pandas as pd


def get_airline_info(name: str) -> dict:
    filename = "../data/group/FlightIncrease/" + name + ".xlsx"
    data = pd.read_excel(filename, sheet_name=None, header=None)
    df = data["Feuil1"].astype(str)
    airline_info = {row[0]: list(row[1:]) for _, row in df.iterrows()}
    for i in airline_info:
        airline_info[i] = [
            x.split(".")[0] if x.endswith(".0") else x
            for x in airline_info[i]
            if x != "nan"
        ]
    return airline_info


def get_group_dict() -> dict:
    group_dict = {"cargo": list(
        set(
            value for sublist in get_airline_info("cargo").values() for value in sublist
        )
    ), "domestic": list(
        set(
            value
            for sublist in get_airline_info("domestic").values()
            for value in sublist
        )
    ), "international": list(
        set(
            value
            for sublist in get_airline_info("international").values()
            for value in sublist
        )
    )}
    return group_dict


class AirlineType:
    cargo = get_airline_info("cargo")
    domestic = get_airline_info("domestic")
    international = get_airline_info("international")
    all_available = get_airline_info("airlinesgate")

    def __init__(self, airline: str):
        self.airline = airline
        self.type = self.get_type()
        self.available_gate = self.get_available_gate()

    def get_type(self) -> str:
        if self.airline in AirlineType.cargo.keys():
            return "cargo"
        elif self.airline in AirlineType.domestic.keys():
            return "domestic"
        elif self.airline in AirlineType.international.keys():
            return "international"
        else:
            print(self.airline)
            raise ValueError("AirlineType.get_type: airline not found")

    def get_available_gate(self) -> list:
        if self.airline in AirlineType.all_available.keys():
            return AirlineType.all_available[self.airline]
        else:
            return []
