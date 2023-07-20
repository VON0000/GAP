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

    def fix_information(self, data, quarter, seuil, delta, interval_flight, interval_data):
        # 所有interval（由data直接计算得到的interval）中，在半小时内的
        half_h = 30 * 60
        q = 15 * 60
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
        # print(interval_flight)
        fix_info = []  # 需要固定的间隔信息
        fix_set = []
        for i in range(len(interval_flight)):
            inter = list(set(flight_list) & set(interval_flight[i]))  # 判断此间隔是否需要固定
            if len(inter) != 0:
                fix_set.append(i)
                fix_info.append([interval_data['begin_callsign'][i], interval_data['registration'][i]])
        # print(fix_info)
        return fix_info

    @staticmethod
    def fix_set(fix_info, interval_data):
        # 按照间隔信息找到对应间隔
        fix_set = []
        for info in fix_info:
            if info[0] in interval_data['begin_callsign']:
                temp = [j for j, values in enumerate(interval_data['begin_callsign']) if values == info[0]]
                if len(temp) == 1:
                    fix_set.append(temp)
                else:
                    index = [values for values in temp if interval_data['registration'][values] == info[1]]
                    fix_set.append(index)
                    # print(interval_data['registration'][temp[0]],
                    #       interval_data['begin_callsign'][temp[0]], interval_data['end_callsign'][temp[0]], '000')
                    # print(interval_data['registration'][temp[1]],
                    #       interval_data['begin_callsign'][temp[1]], interval_data['end_callsign'][temp[1]], '000')
                    # sys.exit(1)
            else:
                pass
        return fix_set

    @staticmethod
    def gate_set(fix_info, fix_set, gate_dict, interval_set):
        # 按照间隔信息找到对应gate
        gate_set = []
        for info in fix_info:
            if info[0] in gate_dict['begin_callsign']:
                temp = [j for j, values in enumerate(gate_dict['begin_callsign']) if values == info[0]]
                if len(temp) == 1:
                    gate_set.append(gate_dict['gate'][temp[0]])
                else:
                    index = [values for values in temp if gate_dict['registration'][values] == info[1]]
                    gate_set.append(gate_dict['gate'][index[0]])
            else:
                pass
        return gate_set


class IfInfeasible(ReallocationInterval):
    def fix_information(self, data, quarter, seuil, delta, interval_flight, interval_data, minutes=None):
        half_h = minutes * 60
        q = 15 * 60
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
        # print(interval_flight)
        fix_info = []  # 需要固定的间隔信息
        fix_set = []
        for i in range(len(interval_flight)):
            inter = list(set(flight_list) & set(interval_flight[i]))  # 判断此间隔是否需要固定
            if len(inter) != 0:
                fix_set.append(i)
                fix_info.append([interval_data['begin_callsign'][i], interval_data['registration'][i]])
        return fix_info


class ReOptimization(Optimization):
    @staticmethod
    def objective(x, n, m, target_matrix, model):
        return model


def reallocation(filename, seuil, part, delta, gate_choose):
    # 初始化
    quarter = 0
    optim_temp = ReOptimization()
    sheetname = optim_temp.find_numbers(filename)
    airline = getdata.load_airlinsgate()
    data = getdata.load_traffic(filename)
    wingsize = getdata.load_wingsize()
    new_interval = ReallocationInterval()
    gate_set = []  # 当前part所用的所有机坪
    result = None
    my_key = ['begin_callsign', 'registration', 'gate']
    default_value = []
    gate_dict = dict.fromkeys(my_key, default_value)

    while quarter < 94:
        # 得到所有interval相关量
        interval = new_interval.presolve(quarter, data, seuil, delta)  # 计算当前quarter下的interval
        second_interval_data = interval[0]
        interval_flight = interval[2]
        # print(second_interval_data['begin_callsign'])

        # 计算当前quarter下的variable，包括x
        variable_set = variable.variable(second_interval_data, airline, wingsize, part, interval_flight, data, quarter)
        interval_data = variable_set[0]
        interval_set_total = variable_set[1]  # 此part用到的所有满足tot和dlt的interval在总共的interval中的索引
        obstruction = variable.get_obstruction(interval_data, interval_set_total)
        temp_x = variable_set[3]
        gate_set = variable_set[2]

        # 验证interval是否都大于零
        for i in range(len(interval_data['interval'])):
            if interval_data['interval'][i] < 0:
                print(interval_data['registration'][i],
                      interval_data['begin_callsign'][i], interval_data['end_callsign'][i], '001')
                sys.exit(1)

        # 计算当前quarter后半小时固定的variable在interval_set(x)中的索引
        total_fix_info = new_interval.fix_information(data, quarter, seuil, delta, interval_flight, interval_data)
        total_fix_list = new_interval.fix_set(total_fix_info, interval_data)
        fix_set = []
        for i in total_fix_list:
            if i in interval_set_total:
                fix_set.append(interval_set_total.index(i))  # 找到当前quarter、当前part下后半小时固定的variable

        # 找到固定的gate
        if quarter == 0:
            gate_fix = []
            for i in fix_set:
                gate_fix.append(gate_choose[i])  # 计算当前固定的variable对应的gate
        else:
            gate_fix = new_interval.gate_set(total_fix_info, fix_set, gate_dict, interval_set_total)

        # 将fix_set中的量固定
        x = variable.actual_x(temp_x, gate_fix, fix_set, gate_set, interval_data, interval_set_total)  # 更新x

        # interval_pr = [value for index, value in enumerate(interval_set_total) if index in fix_set]
        # print(interval_pr, "interval_pr")
        # print(fix_set, "fix_set")
        # print(len(fix_set), "fix_set")
        # print(len(interval_pr), "before remove")
        # for i in interval_pr:
        #     print(second_interval_data['begin_interval'][i],
        #           second_interval_data['end_interval'][i],
        #           second_interval_data['registration'][i],
        #           second_interval_data['begin_callsign'][i],
        #           second_interval_data['end_callsign'][i])

        # 打印出固定的interval以及他们的gate
        temp_list = []
        temp_i1 = []
        # temp_i2 = []
        for i in range(len(x)):
            if sum(x[i]) == 1:
                for temp in range(len(x[i])):
                    if x[i][temp] == 1:
                        temp_list.append(temp)
                        temp_i1.append(interval_data['begin_callsign'][interval_set_total[i]])
                        # temp_i2.append(interval_data['registration'][interval_set_total[i]])
        print(len(temp_i1), temp_i1, 'x list')
        # print(temp_i2, "x list")
        print(temp_list, "x gate")
        print(len(interval_set_total))

        # 优化
        target_matrix = []
        result = optim_temp.optim(x, obstruction, target_matrix, part)  # 优化
        status = result[3]
        gate_choose = result[1]

        # 构建gate和interval的对应dict
        temp_1 = []
        temp_2 = []
        temp_3 = []
        for i in range(len(gate_choose)):
            index = interval_set_total[i]
            temp_1.append(interval_data['begin_callsign'][index])
            temp_2.append(interval_data['registration'][index])
            temp_3.append(gate_choose[i])
        my_key = ['begin_callsign', 'registration', 'gate']
        default_value = []
        gate_dict = dict.fromkeys(my_key, default_value)
        gate_dict['begin_callsign'] = temp_1
        gate_dict['registration'] = temp_2
        gate_dict['gate'] = temp_3

        # 无解时
        t = 0
        counter = 0
        pr_temp = []
        while status == 3 and counter < 3:  # t >= 30
            if_interval = IfInfeasible()
            delta_temp = -5
            interval = if_interval.presolve(quarter, data, seuil, delta_temp)  # 计算当前quarter下的interval
            second_interval_data = interval[0]
            # print(second_interval_data)
            # 计算当前quarter下的variable
            variable_set = variable.variable_infeasible(second_interval_data, airline, wingsize, part, quarter,
                                                        interval_set_total, counter, pr_temp)
            interval_data = variable_set[0]  # 所有interval的数据
            interval_set = variable_set[1]  # 一小时内的interval集合
            obstruction = variable.get_obstruction(interval_data, interval_set)
            for i in range(len(interval_data['interval'])):
                if interval_data['interval'][i] < 0:
                    print(interval_data['registration'][i],
                          interval_data['begin_callsign'][i], interval_data['end_callsign'][i], '001')
                    sys.exit(1)
            temp_x = variable_set[3]
            gate_set = variable_set[2]

            # 计算当前quarter后半小时固定的variable
            total_fix_info = if_interval.fix_information(data, quarter, seuil, delta_temp,
                                                         interval_flight, interval_data, t)
            total_fix_list = if_interval.fix_set(total_fix_info, interval_data)
            fix_set = []
            for i in total_fix_list:
                if i in interval_set:
                    # 找到当前quarter、当前part下后半小时固定的variable fix_set是interval_set中的索引
                    fix_set.append(interval_set.index(i))
            x = variable.actual_x(temp_x, gate_fix, fix_set, gate_set, interval_data, interval_set)  # 更新x

            interval_pr = [value for index, value in enumerate(interval_set) if index not in fix_set]  # 在所有interval中的索引
            pr_temp.append(interval_pr)
            # print(interval_pr, "interval_pr")
            # print(fix_set, "fix_set")
            # print(interval_set, "interval_set")
            print(len(fix_set), "fix_set")
            print(len(interval_set), "before remove")
            for i in interval_pr:
                print(second_interval_data['begin_interval'][i],
                      second_interval_data['end_interval'][i],
                      second_interval_data['registration'][i],
                      second_interval_data['begin_callsign'][i],
                      second_interval_data['end_callsign'][i])

            temp_list = []
            temp_i1 = []
            for i in range(len(x)):
                if sum(x[i]) == 1:
                    for temp in range(len(x[i])):
                        if x[i][temp] == 1:
                            temp_list.append(temp)
                            temp_i1.append(interval_data['begin_callsign'][interval_set[i]])
            print(len(temp_i1), temp_i1, 'x list')
            print(temp_list, "x gate")
            target_matrix = []
            result = optim_temp.optim(x, obstruction, target_matrix, part)  # 优化
            temp = result[1]
            if temp is None:
                pass
            else:
                gate_choose = []
                for i in interval_set_total:
                    if i in interval_set:
                        j = interval_set.index(i)
                        gate_choose.append(temp[j])
                    else:
                        gate_choose.append([])
            status = result[3]
            print(t, "relaxation of optimization conditions")
            t = 30
            counter = counter + 1

        quarter += 1
        print(quarter)

    outputdata.write_xls(result, sheetname, gate_set)
    gate_choose = result[1]
    return gate_choose
