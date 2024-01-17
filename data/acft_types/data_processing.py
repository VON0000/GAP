import re

import pandas as pd
import xlwt


def get_acft_types_data():
    filename = "./acft_types"
    with open(filename, "r", encoding='gbk') as f:
        data = f.read()
    return data


def split_data(data):
    splitted_strings = data.split("\n")
    return splitted_strings


def output(splitted_strings):
    data_dict = {"Aircraft Model": [], "Engine Type": [], "Aircraft Type": []}

    for i, segment in enumerate(splitted_strings):
        if segment != "":
            match = re.match(r'^[^ ]+', segment)
            data_dict["Aircraft Model"].append(match.group(0))
            data_dict["Engine Type"].append(segment[-2])
            data_dict["Aircraft Type"].append(segment[-1])

    data_frame = pd.DataFrame(data_dict)

    file_name = "./acft_types.csv"
    data_frame.to_csv(file_name, index=False, encoding='gbk')


if __name__ == "__main__":
    data = get_acft_types_data()
    split_data(data)
    output(split_data(data))
