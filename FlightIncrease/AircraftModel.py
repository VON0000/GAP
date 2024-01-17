def get_aircraft_model() -> dict:
    filename = "../data/acft_types/acft_types.csv"

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
    def __init__(self):
        self.model = ...
        self.engine_type = ...
        self.aircraft_type = ...


if __name__ == "__main__":
    get_aircraft_model()
