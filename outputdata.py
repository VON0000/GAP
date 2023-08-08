import sys

import xlwt
import pandas as pd


def write_xls(gate_dict, sheetname, gate_set, interval_data, interval_set):
    sheetname = ' '.join(sheetname)

    wb = xlwt.Workbook()
    # 添加一个表
    ws = wb.add_sheet(sheetname)

    # 3个参数分别为行号，列号，和内容
    # 需要注意的是行号和列号都是从0开始的
    ws.write(0, 0, 'call_sign_1')
    ws.write(0, 1, 'call_sign_2')
    ws.write(0, 2, 'registration')
    ws.write(0, 3, 'gate')
    ws.write(0, 4, 'begin time')
    ws.write(0, 5, 'finish time')

    for i in range(len(gate_dict['gate'])):
        ws.write(i + 1, 0, gate_dict['begin_callsign'][i])
        try:
            ws.write(i + 1, 1, gate_dict['end_callsign'][i])
        except KeyError:
            pass
        ws.write(i + 1, 2, gate_dict['registration'][i])
        ws.write(i + 1, 3, gate_set[gate_dict['gate'][i]])
        ws.write(i + 1, 4, interval_data['begin_interval'][interval_set[i]])
        ws.write(i + 1, 5, interval_data['end_interval'][interval_set[i]])

    # 保存excel文件
    wb.save('./results/buffer/result.xls')


def write_interval(result, sheetname):
    sheetname = ' '.join(sheetname)
    interval_data = result[0]

    wb = xlwt.Workbook()
    # 添加一个表
    ws = wb.add_sheet(sheetname)

    # 3个参数分别为行号，列号，和内容
    # 需要注意的是行号和列号都是从0开始的
    my_key = ['interval', 'begin_interval', 'end_interval', 'airline', 'registration', 'begin_callsign',
              'end_callsign', 'wingspan']
    for i in range(len(my_key)):
        ws.write(0, i, my_key[i])

    for i in range(len(my_key)):
        for j in range(len(interval_data['interval'])):
            ws.write(j + 1, i, interval_data[my_key[i]][j])

    # 保存excel文件
    wb.save('./results/buffer/interval.xls')


def write_final(gate_dict, sheetname, gate_set, pattern, regulation, in_name):
    if regulation == 1:
        name = sheetname + ['ZBTJ', 'MANEX']
    elif regulation == 2:
        name = sheetname + ['ZBTJ', 'MIN']
    elif regulation == 3:
        name = sheetname + ['ZBTJ-PN', 'MANEX']
    else:
        name = sheetname + ['ZBTJ-PN', 'MIN']

    name = '_'.join(name)
    out_name = ['./results/buffer/', name, '.csv']
    output_file_path = ''.join(out_name)
    input_file_path = in_name

    data = pd.read_csv(input_file_path)

    # 指定要更改的列名
    column_name_to_change = 'QFU'  # 将 'column_name' 替换为实际的列名

    if len(pattern) != len(data[column_name_to_change]):
        print('the length of pattern is not equal to the length of data')
        sys.exit(1)

    # 使用 for 循环遍历每一行并修改指定列的值
    for index, row in data.iterrows():
        if pattern[index] == 1:
            new_value = '16R'
        elif pattern[index] == 2:
            new_value = '16L'
        else:
            new_value = '16R'
        data.loc[index, column_name_to_change] = new_value

    # 指定要更改的列名
    column_name_to_change = 'Parking'  # 将 'column_name' 替换为实际的列名

    # 读取原始 CSV 文件并修改指定列的数据
    data[column_name_to_change] = None

    for i in range(len(gate_dict['gate'])):
        call_sign1 = gate_dict['begin_callsign'][i]
        call_sign2 = gate_dict['end_callsign'][i]
        registration = gate_dict['registration'][i]
        if call_sign1 == call_sign2:
            front_part = call_sign1[:-2]
            front_part = front_part.rstrip()
            last_two_chars = call_sign1[-2:]
            data = new_data(data, front_part, gate_set, gate_dict, i, registration, last_two_chars)
        else:
            front_part1 = call_sign1[:-2]
            front_part1 = front_part1.rstrip()
            last_two_chars1 = call_sign1[-2:]
            front_part2 = call_sign2[:-2]
            front_part2 = front_part2.rstrip()
            last_two_chars2 = call_sign2[-2:]
            data = new_data(data, front_part1, gate_set, gate_dict, i, registration, last_two_chars1)
            data = new_data(data, front_part2, gate_set, gate_dict, i, registration, last_two_chars2)
    # 将修改后的数据保存为新的 CSV 文件
    data.to_csv(output_file_path, index=False)


def new_data(data, front_part, gate_set, gate_dict, i, registration, last_two_chars):
    choose_list1 = []
    for j, row in data.iterrows():
        if data.loc[j, 'callsign'] == front_part:
            choose_list1.append(j)
    if len(choose_list1) == 1:
        new_value = gate_set[gate_dict['gate'][i]]
        data.loc[choose_list1[0], 'Parking'] = new_value
    else:
        choose_list2 = []
        for k in choose_list1:
            if data.loc[k, 'registration'] == registration:
                choose_list2.append(k)
        if len(choose_list2) == 1:
            new_value = gate_set[gate_dict['gate'][i]]
            data.loc[choose_list2[0], 'Parking'] = new_value
        else:
            for c in choose_list2:
                if data.loc[c, 'departure'] == 'ZBTJ' and last_two_chars == 'de':
                    new_value = gate_set[gate_dict['gate'][i]]
                    data.loc[c, 'Parking'] = new_value
                else:
                    new_value = gate_set[gate_dict['gate'][i]]
                    data.loc[c, 'Parking'] = new_value
    return data
