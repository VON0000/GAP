import numpy as np


def get_aircraft_model() -> dict:
    filename = "./data/acft_types/acft_types.csv"

    with open(filename, 'r') as file:
        lines = file.readlines()

    aircraft_model = {"model": [], "engine_type": [], "aircraft_type": []}

    for i, line in enumerate(lines):
        if i != 0:
            line = line.split(",")
            aircraft_model["model"].append(line[0])
            aircraft_model["engine_type"].append(line[1])
            aircraft_model["aircraft_type"].append(line[2].strip("\n"))

    return aircraft_model


class AircraftModel:
    aircraft_model = get_aircraft_model()

    def __init__(self, model: str):
        self.model = model
        self.engine_type = self._get_engine_type()
        self.aircraft_type = self._get_aircraft_type()

    def _get_engine_type(self, ) -> str:
        index = np.where(np.array(AircraftModel.aircraft_model["model"]) == self.model)[0][0]
        engine_type = AircraftModel.aircraft_model["engine_type"][index]
        return engine_type

    def _get_aircraft_type(self) -> str:
        index = np.where(np.array(AircraftModel.aircraft_model["model"]) == self.model)[0][0]
        aircraft_type = AircraftModel.aircraft_model["aircraft_type"][index]
        return aircraft_type
