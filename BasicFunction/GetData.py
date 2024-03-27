import pandas as pd


def get_data(filename) -> dict:
    data = pd.read_csv(filename)
    data = data.to_dict(orient="list")
    for i in range(len(data["data"])):
        if data["arrivee"][i] == "ZBTJ":
            data["callsign"][i] = data["callsign"][i] + " ar"
        else:
            data["callsign"][i] = data["callsign"][i] + " de"
    return data
