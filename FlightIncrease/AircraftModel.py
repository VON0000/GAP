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


def get_model_inst_list() -> list:
    aircraft_model = get_aircraft_model()
    model_inst_list = []
    for i in range(len(aircraft_model["model"])):
        model_inst_list.append(
            AircraftModel(
                aircraft_model["model"][i],
                aircraft_model["engine_type"][i],
                aircraft_model["aircraft_type"][i],
            )
        )
    return model_inst_list


class AircraftModel:
    def __init__(self, model: str, engine_type: str, aircraft_type: str):
        self.model = model
        self.engine_type = engine_type
        self.aircraft_type = aircraft_type


if __name__ == "__main__":
    get_model_inst_list()
