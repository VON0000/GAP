import os

from BasicFunction.GetInterval import GetInterval

if __name__ == "__main__":

    folder_path = "../results/Traffic_GAP_2Pistes"

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            filename = os.path.join(folder_path, filename)
            ...
