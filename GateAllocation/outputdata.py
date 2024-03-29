import sys

import pandas as pd


def get_name(regulation, sheetname):
    if regulation == 1:
        name = sheetname + ['ZBTJ', 'MANEX']
    elif regulation == 2:
        name = sheetname + ['ZBTJ', 'MIN']
    elif regulation == 3:
        name = sheetname + ['ZBTJ-PN', 'MANEX']
    else:
        name = sheetname + ['ZBTJ-PN', 'MIN']
    name = '_'.join(name)
    return name


class ToCsv:
    """
    Export the results to a CSV file
    """

    def write_final(self, gate_dict, sheetname, gate_set, pattern, regulation, in_name, counter, remote_number):
        name = get_name(regulation, sheetname)
        out_name = ['./results/Traffic_GAP_2Pistes/', name, '.csv']
        in_name = ['./results/Traffic_GAP_2Pistes/', name, '.csv']
        output_file_path = ''.join(out_name)
        # input_file_path = in_name
        input_file_path = ''.join(in_name)

        data = pd.read_csv(input_file_path)

        for i in range(len(gate_dict['gate'])):
            call_sign1 = gate_dict['begin_callsign'][i]
            call_sign2 = gate_dict['end_callsign'][i]
            registration = gate_dict['registration'][i]
            if call_sign1 == call_sign2:
                front_part = call_sign1[:-2]
                front_part = front_part.rstrip()
                last_two_chars = call_sign1[-2:]
                data = self.new_data(data, front_part, gate_set, gate_dict, i, registration, last_two_chars)
            else:
                front_part1 = call_sign1[:-2]
                front_part1 = front_part1.rstrip()
                last_two_chars1 = call_sign1[-2:]
                front_part2 = call_sign2[:-2]
                front_part2 = front_part2.rstrip()
                last_two_chars2 = call_sign2[-2:]
                data = self.new_data(data, front_part1, gate_set, gate_dict, i, registration, last_two_chars1)
                data = self.new_data(data, front_part2, gate_set, gate_dict, i, registration, last_two_chars2)
                data = self.change_data(data, front_part2, gate_dict, i, registration, last_two_chars2)

        # 指定要更改的列名
        column_name_to_change = 'changing times'  # 将 'column_name' 替换为实际的列名

        # 读取原始 CSV 文件并修改指定列的数据
        data.loc[0, column_name_to_change] = counter

        # 指定要更改的列名
        column_name_to_change = 'remote numbers'  # 将 'column_name' 替换为实际的列名

        # 读取原始 CSV 文件并修改指定列的数据
        data.loc[0, column_name_to_change] = remote_number
        # 将修改后的数据保存为新的 CSV 文件
        data.to_csv(output_file_path, index=False)

    @staticmethod
    def change_data(data, front_part, gate_dict, i, registration, last_two_chars):
        assert last_two_chars == 'de', 'the last two chars is not de'
        for j, row in data.iterrows():
            if (data.loc[j, 'callsign'] == front_part
                    and data.loc[j, 'registration'] == registration
                    and data.loc[j, 'departure'] == 'ZBTJ'):
                new_value = gate_dict['end_interval'][i] * 30 + 5 * 60
                data.loc[j, 'ATOT'] = new_value
                break
        return data

    @staticmethod
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
                    elif data.loc[c, 'arrivee'] == 'ZBTJ' and last_two_chars == 'ar':
                        new_value = gate_set[gate_dict['gate'][i]]
                        data.loc[c, 'Parking'] = new_value
                    else:
                        continue
        return data

    def write_other(self, gate_dict, filename, sheetname, gate_set, pattern, regulation):
        """

        this one is to record other regulations
        """
        name = get_name(regulation, sheetname)
        out_name = ['../results/Traffic_GAP_test/', name, '.csv']
        output_file_path = ''.join(out_name)

        data = pd.read_csv(filename)
        # data = pd.read_csv(output_file_path)

        data = for_new_file(pattern, data)

        for i in range(len(gate_dict['gate'])):
            call_sign1 = gate_dict['begin_callsign'][i]
            call_sign2 = gate_dict['end_callsign'][i]
            registration = gate_dict['registration'][i]
            if call_sign1 == call_sign2:
                front_part = call_sign1[:-2]
                front_part = front_part.rstrip()
                last_two_chars = call_sign1[-2:]
                data = self.new_data(data, front_part, gate_set, gate_dict, i, registration, last_two_chars)
            else:
                front_part1 = call_sign1[:-2]
                front_part1 = front_part1.rstrip()
                last_two_chars1 = call_sign1[-2:]
                front_part2 = call_sign2[:-2]
                front_part2 = front_part2.rstrip()
                last_two_chars2 = call_sign2[-2:]
                data = self.new_data(data, front_part1, gate_set, gate_dict, i, registration, last_two_chars1)
                data = self.new_data(data, front_part2, gate_set, gate_dict, i, registration, last_two_chars2)
                data = self.change_data(data, front_part2, gate_dict, i, registration, last_two_chars2)
        # 将修改后的数据保存为新的 CSV 文件
        data.to_csv(output_file_path, index=False)

    def write_process(self, gate_dict, sheetname, gate_set, regulation, quarter):
        """

        this is for the GenerateSolution.py, which is used to record the first time of the allocation
        """

        name = get_name(regulation, sheetname)
        out_name = ['../results/Traffic_GAP_test/', name, '_process.csv']
        in_name = ['../results/Traffic_GAP_2Pistes/', name, '.csv']
        output_file_path = ''.join(out_name)
        input_file_path = ''.join(in_name)

        data = pd.read_csv(input_file_path)
        data = data.drop(['TTOT'], axis=1)
        data = data.drop(['TLDT'], axis=1)
        data = data.drop(['ATOT'], axis=1)
        data = data.drop(['ALDT'], axis=1)
        data = data.drop(['Type'], axis=1)
        data = data.drop(['Wingspan'], axis=1)
        data = data.drop(['Airline'], axis=1)
        data = data.drop(['QFU'], axis=1)
        temp = data.loc[:, 'Parking']
        data = data.drop(['Parking'], axis=1)
        data['Parking'] = temp

        for i in range(len(gate_dict['gate'])):
            call_sign1 = gate_dict['begin_callsign'][i]
            call_sign2 = gate_dict['end_callsign'][i]
            registration = gate_dict['registration'][i]
            if call_sign1 == call_sign2:
                front_part = call_sign1[:-2]
                front_part = front_part.rstrip()
                last_two_chars = call_sign1[-2:]
                data = self.new_data(data, front_part, gate_set, gate_dict, i, registration, last_two_chars)
            else:
                front_part1 = call_sign1[:-2]
                front_part1 = front_part1.rstrip()
                last_two_chars1 = call_sign1[-2:]
                front_part2 = call_sign2[:-2]
                front_part2 = front_part2.rstrip()
                last_two_chars2 = call_sign2[-2:]
                data = self.new_data(data, front_part1, gate_set, gate_dict, i, registration, last_two_chars1)
                data = self.new_data(data, front_part2, gate_set, gate_dict, i, registration, last_two_chars2)
        data.to_csv(output_file_path, index=False)


class ProcessToCsv(ToCsv):
    @staticmethod
    def new_data(data, front_part, gate_set, gate_dict, i, registration, last_two_chars, quarter=None):
        parking = 'Parking' + str(quarter)
        choose_list1 = []
        for j, row in data.iterrows():
            if data.loc[j, 'callsign'] == front_part:
                choose_list1.append(j)
        if len(choose_list1) == 1:
            new_value = gate_set[gate_dict['gate'][i]]
            data.loc[choose_list1[0], parking] = new_value
        else:
            choose_list2 = []
            for k in choose_list1:
                if data.loc[k, 'registration'] == registration:
                    choose_list2.append(k)
            if len(choose_list2) == 1:
                new_value = gate_set[gate_dict['gate'][i]]
                data.loc[choose_list2[0], parking] = new_value
            else:
                for c in choose_list2:
                    if data.loc[c, 'departure'] == 'ZBTJ' and last_two_chars == 'de':
                        new_value = gate_set[gate_dict['gate'][i]]
                        data.loc[c, parking] = new_value
                    elif data.loc[c, 'arrivee'] == 'ZBTJ' and last_two_chars == 'ar':
                        new_value = gate_set[gate_dict['gate'][i]]
                        data.loc[c, parking] = new_value
                    else:
                        continue
        return data

    @staticmethod
    def read_process(sheetname, regulation):
        name = get_name(regulation, sheetname)
        in_name = ['../results/Traffic_GAP_2Pistes/', name, '_process.csv']
        input_file_path = ''.join(in_name)

        process_data = pd.read_csv(input_file_path)

        return process_data

    def write_process(self, gate_dict, sheetname, gate_set, regulation, process_data, quarter=None):
        """

        this one is for the reallocation.py, which is used to record the reallocation
        """
        last_col_name = process_data.columns[-1]
        process_data['Parking' + str(quarter)] = process_data[last_col_name]

        for i in range(len(gate_dict['gate'])):
            call_sign1 = gate_dict['begin_callsign'][i]
            call_sign2 = gate_dict['end_callsign'][i]
            registration = gate_dict['registration'][i]
            if call_sign1 == call_sign2:
                front_part = call_sign1[:-2]
                front_part = front_part.rstrip()
                last_two_chars = call_sign1[-2:]
                process_data = self.new_data(process_data, front_part, gate_set, gate_dict, i, registration,
                                             last_two_chars, quarter)
            else:
                front_part1 = call_sign1[:-2]
                front_part1 = front_part1.rstrip()
                last_two_chars1 = call_sign1[-2:]
                front_part2 = call_sign2[:-2]
                front_part2 = front_part2.rstrip()
                last_two_chars2 = call_sign2[-2:]
                process_data = self.new_data(process_data, front_part1, gate_set, gate_dict, i, registration,
                                             last_two_chars1, quarter)
                process_data = self.new_data(process_data, front_part2, gate_set, gate_dict, i, registration,
                                             last_two_chars2, quarter)
        return process_data

    @staticmethod
    def write_process_to_file(process_data, regulation, sheetname):
        name = get_name(regulation, sheetname)
        out_name = ['../results/Traffic_GAP_test/', name, '_process.csv']
        output_file_path = ''.join(out_name)

        process_data.to_csv(output_file_path, index=False)


def for_new_file(pattern, data):
    # 指定要更改的列名
    column_name_to_change = 'QFU'  # 将 'column_name' 替换为实际的列名

    if len(pattern) != len(data[column_name_to_change]):
        print('the length of pattern is not equal to the length of data',
              len(pattern), len(data[column_name_to_change]))
        sys.exit(1)

    # 使用 for 循环遍历每一行并修改指定列的值
    for index, row in data.iterrows():
        if pattern[index] == 2:
            new_value = '16L'
        else:
            new_value = '16R'
        data.loc[index, column_name_to_change] = new_value

    # 指定要更改的列名
    column_name_to_change = 'Parking'  # 将 'column_name' 替换为实际的列名

    # 读取原始 CSV 文件并修改指定列的数据
    data[column_name_to_change] = None
    return data
