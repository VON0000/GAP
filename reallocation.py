import getdata
from getinterval import GetInterval
import variable
from optimization import Optimization
import outputdata
import numpy as np
import sys


class ReGetInterval(GetInterval):
    def taxiing_pattern(self, t_or_a, seuil, data):
        n = len(data['data'])
        pattern = [0] * n
        return pattern


class ReallocationInterval(ReGetInterval):
    @staticmethod
    def actual_target(data, quarter):
        departure_set = np.where(data['departure'] == 'ZBTJ')[0]
        h = 60 * 60
        q = 15 * 60
        n = len(data['data'])
        tot = data['TTOT']
        ldt = data['TLDT']
        for i in range(n):
            if i in departure_set:
                if data['ATOT'][i] <= quarter * q + h:
                    tot[i] = data['ATOT'][i]
            else:
                if data['ALDT'][i] <= quarter * q + h:
                    ldt[i] = data['ALDT'][i]
        return tot, ldt

    def fix_infomation(self, data, quarter, seuil, delta):
        half_h = 30 * 60
        q = 15 * 50
        n = len(data['data'])
        flight_list = []  # 计算需要固定的航班序列
        departure_set = np.where(data['departure'] == 'ZBTJ')[0]
        for i in range(n):
            if i in departure_set:
                if data['ATOT'][i] <= quarter * q + half_h:
                    flight_list.append(i)
            else:
                if data['ALDT'][i] <= quarter * q + half_h:
                    flight_list.append(i)
        # print(flight_list)
        temp = self.presolve(quarter, data, seuil, delta)
        interval_flight = temp[2]  # 每个间隔相关的航班
        interval_data = temp[0]
        # print(interval_flight)
        fix_info = []  # 需要固定的间隔信息
        fix_set = []
        for i in range(len(interval_flight)):
            inter = list(set(flight_list) & set(interval_flight[i]))  # 判断此间隔是否需要固定
            if len(inter) != 0:
                fix_info.append(i)
                fix_set.append(interval_data['registration'][i])
        # print(fix_set)
        return fix_info

    # def fix_set(self, fix_info, interval, quarter, data, seuil, delta):
    #     # 按照间隔信息找到对应间隔
    #     temp = self.presolve(quarter, data, seuil, delta)
    #     interval_data = temp[0]
    #     for info in fix_info:
    #         temp_1 = interval_data['registrationl'].index(info[0])
    #         temp_2 = interval_data['begin_callsign'].index(info[1])
    #         temp_3 = interval_data['end_callsign'].index(info[2])


class ReOptimization(Optimization):
    @staticmethod
    def objective(x, n, m, target_matrix, model):
        return model


def reallocation(filename, seuil, part, delta, gate_choose):
    quarter = 0
    optim_temp = ReOptimization()
    sheetname = optim_temp.find_numbers(filename)
    airline = getdata.load_airlinsgate()
    data = getdata.load_traffic(filename)
    wingsize = getdata.load_wingsize()
    new_interval = ReallocationInterval()
    gate_fix = []
    gate_set = []  # 当前part所用的所有机坪
    result = None
    while quarter < 7:
        interval = new_interval.presolve(quarter, data, seuil, delta)  # 计算当前quarter下的interval
        second_interval_data = interval[0]
        variable_set = variable.variable(second_interval_data, airline, wingsize, part)  # 计算当前quarter下的variable
        interval_data = variable_set[0]
        interval_set = variable_set[1]
        obstruction = variable.get_obstruction(interval_data, interval_set)
        for i in range(len(interval_data['interval'])):
            if interval_data['interval'][i] < 0:
                print(interval_data['registration'][i],
                      interval_data['begin_callsign'][i], interval_data['end_callsign'][i])
                sys.exit(1)
        temp_x = variable_set[3]
        gate_set = variable_set[2]
        total_fix_list = new_interval.fix_infomation(data, quarter, seuil, delta)  # 计算当前quarter后半小时固定的variable
        used_interval = variable_set[1]  # 此part用到的所有interval
        fix_set = []
        fix_info = []
        for i in total_fix_list:
            if i in used_interval:
                fix_set.append(used_interval.index(i))  # 找到当前quarter、当前part下后半小时固定的variable
                fix_info.append(interval_data['registration'][i])
        print(fix_info, "apres")
        print(fix_set)
        if quarter == 0:
            gate_fix = []
            for i in fix_set:
                gate_fix.append(gate_choose[i])  # 计算当前固定的variable对应的gate
        print(gate_fix, "apres")
        x = variable.actual_x(temp_x, gate_fix, fix_set, gate_set, interval_data)  # 更新x
        temp_list = []
        temp_i = []
        print(len(x))
        for i in range(len(x)):
            if sum(x[i]) == 1:
                for temp in range(len(x[i])):
                    if x[i][temp] == 1:
                        temp_list.append(temp)
                        temp_i.append(interval_data['registration'][i])
        print(temp_i, 'x list')
        print(temp_list, "x gate")
        target_matrix = []
        result = optim_temp.optim(x, obstruction, target_matrix, part)  # 优化
        quarter += 1
        print(quarter)
        gate_choose = result[1]
        total_fix_info = new_interval.fix_infomation(data, quarter, seuil, delta)  # 计算当前quarter后半小时固定的variable
        # print(total_fix_info)
        used_interval = variable_set[1]
        fix_set = []
        fix_info = []
        for i in total_fix_info:
            if i in used_interval:
                fix_set.append(used_interval.index(i))  # 找到当前quarter、当前part下后半小时固定的variable
                fix_info.append(interval_data['registration'][i])
        gate_fix = []
        print(fix_info, "avant")
        for i in fix_set:
            gate_fix.append(gate_choose[i])  # 计算当前固定的variable对应的gate
        print(gate_fix, "avant")
    outputdata.write_xls(result, sheetname, gate_set)
    gate_choose = result[1]
    return gate_choose
