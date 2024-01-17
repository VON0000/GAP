import re

import xlwt


def get_acft_types_data():
    filename = "./acft_types"
    with open(filename, "r") as f:
        data = f.read()
    return data


def split_data(data):
    splitted_strings = data.split("\n")
    return splitted_strings


def output(splitted_strings):
    wb = xlwt.Workbook()
    ws = wb.add_sheet("acft_types")

    ws.write(0, 0, "Aircraft Model")
    ws.write(0, 1, "Engine Type")
    ws.write(0, 2, "Aircraft Type")

    for i, segment in enumerate(splitted_strings):
        if segment != "":
            match = re.match(r'^[^ ]+', segment)
            ws.write(i + 1, 0, match.group())
            ws.write(i + 1, 1, segment[-2])
            ws.write(i + 1, 2, segment[-1])

    file_name = "./acft_types.csv"
    wb.save(file_name)


if __name__ == "__main__":
    data = get_acft_types_data()
    split_data(data)
    output(split_data(data))
