import os

from BasicFunction.GetData import get_data
from refactorGateAllocation.GateAllocation import GateAllocation

if __name__ == "__main__":

    folder_path = "../results/Traffic_GAP_2Pistes"
    seuil = 28
    pattern = "MANEX"

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            filename = os.path.join(folder_path, filename)

            data = get_data(filename)
            GateAllocation(data, seuil, pattern).optimization()
