import getdata
from getinterval import GetInterval
import variable
from optimization import Optimization
from taxiingtime_matrix import ReMatrix
import numpy as np
import sys
# import localsearch
# import plot
from outputdata import ToCsv
from outputdata import ProcessToCsv


class ReGetInterval(GetInterval):
    def taxiing_pattern(self, t_or_a, seuil, data):
        t_or_a = 0
        pattern = super().taxiing_pattern(t_or_a, seuil, data)
        return pattern


class ReallocationInterval(ReGetInterval):
    """
    determine specific intervals that should remain unchanged
    and fix the parking stands assigned to them.
    """
    @staticmethod
    def fix_information(data, quarter, seuil, delta, interval_flight, interval_data):
        # 所有interval（由data直接计算得到的interval）中，在半小时内的
        half_h = 30 * 60
        q = 15 * 60
        n = len(data['data'])
        flight_list = []  # 计算需要固定的航班序列
        departure = np.array(data['departure'])
        departure_set = np.where(departure == 'ZBTJ')[0]
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
    def gate_set(fix_info, gate_dict):
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


# class IfInfeasible(ReallocationInterval):
#     def fix_information(self, data, quarter, seuil, delta, interval_flight, interval_data, minutes=None):
#         print(minutes, "minutes")
#         half_h = minutes * 60
#         q = 15 * 60
#         n = len(data['data'])
#         flight_list = []  # 计算需要固定的航班序列
#         departure = np.array(data['departure'])
#         departure_set = np.where(departure == 'ZBTJ')[0]
#         for i in range(n):
#             if i in departure_set:
#                 if data['ATOT'][i] <= quarter * q + half_h:
#                     flight_list.append(i)
#             else:
#                 if data['ALDT'][i] <= quarter * q + half_h:
#                     flight_list.append(i)
#         # print(interval_flight)
#         fix_info = []  # 需要固定的间隔信息
#         fix_set = []
#         for i in range(len(interval_flight)):
#             inter = list(set(flight_list) & set(interval_flight[i]))  # 判断此间隔是否需要固定
#             if len(inter) != 0:
#                 fix_set.append(i)
#                 fix_info.append([interval_data['begin_callsign'][i], interval_data['registration'][i]])
#         return fix_info


# class ReOptimization(Optimization):
#     @staticmethod
#     def objective(x, n, m, target_matrix, model):
#         return model


def find_obstruction(fix_set, obstruction, interval_data, interval_set, quarter, gate_fix):
    """

    Whether there are conflicts within the part of the solution that has been fixed
    """
    dependent_dic = Optimization.dependent_gate()
    dependent_set = Optimization.dependent_set()

    question = -1
    flag = 1000
    for i in fix_set:
        idx = interval_set[i]
        begin_time = interval_data['begin_interval'][idx]
        if begin_time < quarter * 15 * 2:
            continue
        else:
            gate = gate_fix[fix_set.index(i)]
            if gate not in dependent_set:
                fix_avant = []
                for f in range(len(fix_set)):
                    gate_temp = gate_fix[f]
                    if gate_temp == gate:
                        fix_avant.append(fix_set[f])
                local_obstruction = obstruction[i]
                temp = list(set(local_obstruction) & set(fix_avant))
            else:
                fix_avant = []
                for f in range(len(fix_set)):
                    gate_temp = gate_fix[f]
                    index = np.where(np.array(dependent_dic['gate']) == gate)[0][0]
                    new_gate_list = [gate] + dependent_dic['dependent'][index]
                    if gate_temp in new_gate_list:
                        fix_avant.append(fix_set[f])
                local_obstruction = obstruction[i]
                temp = list(set(local_obstruction) & set(fix_avant))
            if len(temp) == 0:
                continue
            else:
                if begin_time > question:
                    question = begin_time
                    flag = i
    if question != -1:
        gate_fix.pop(fix_set.index(flag))
        fix_set.remove(flag)
    return fix_set, gate_fix


def change_times(old_gate_dic, gate_dict, counter):
    """

    How many times were parking stands changed
    """
    n = len(gate_dict['gate'])
    for i in range(n):
        list_1 = [index for index, value in enumerate(old_gate_dic['begin_callsign'])
                  if value == gate_dict['begin_callsign'][i]]
        list_2 = [index for index, value in enumerate(old_gate_dic['registration'])
                  if value == gate_dict['registration'][i]]
        k = list(set(list_1) & set(list_2))
        if not k:
            continue
        else:
            k = k[0]
            if old_gate_dic['gate'][k] != gate_dict['gate'][i]:
                counter += 1
    return counter


def final_remote(gate_dict, airline, interval_data, gate_set):
    """

    How many aircraft have been allocated to remote stands at the end of the iteration
    """
    remote_number = 0
    n = len(gate_dict['gate'])
    for i in range(n):
        index = [j for j, x in enumerate(interval_data['registration']) if x == gate_dict['registration'][i]]
        company = interval_data['airline'][index[0]]
        company_gate = airline[company]
        company_gate = [i for i, x in enumerate(gate_set) if x in company_gate]
        if gate_dict['gate'][i] in company_gate:
            continue
        else:
            remote_number += 1
    return remote_number


def reallocation(filename, seuil, part, delta, gate_dict, regulation, pattern):
    """

    Every 15 minutes, update the actual time and reassign parking stands.
    """
    # Initialize
    counter = 0
    quarter = 0
    optim_temp = Optimization()
    new_interval = ReallocationInterval()
    gate_set = []
    interval_data = None
    matrix = ReMatrix()
    to_csv = ToCsv()
    process_to_csv = ProcessToCsv()
    sheetname = optim_temp.find_numbers(filename)

    # Import data
    airline = getdata.load_airlinsgate()
    data = getdata.load_traffic(filename)
    wingsize = getdata.load_wingsize()
    taxiingtime = getdata.load_taxitime(regulation)

    # Initial solution
    genernate = gate_dict

    while quarter < 94:
        # Obtain all interval-related data
        interval = new_interval.presolve(quarter, data, seuil, delta)  # Intervals for the current quarter
        second_interval_data = interval[0]
        interval_pattern = interval[1]
        interval_flight = interval[2]
        # print(second_interval_data['begin_callsign'])

        # Variables for the current quarter, including x
        variable_set = variable.variable(second_interval_data, airline, wingsize, part, interval_flight, data, quarter)
        interval_data, interval_set, gate_set, temp_x = variable_set
        # interval set -> The indices of intervals satisfying 'tot' and 'dlt' criteria used in this part
        #                 within the total set of intervals.

        # conflicts
        obstruction = variable.get_obstruction(interval_data, interval_set)

        # Check if intervals are all greater than zero
        # TODO:assert
        for i in range(len(interval_data['interval'])):
            if interval_data['interval'][i] <= 0:
                print(interval_data['registration'][i],
                      interval_data['begin_callsign'][i], interval_data['end_callsign'][i], '001')
                sys.exit(1)

        # The indices of fixed variables (quarter + 30 minutes) in the interval_set(x)
        total_fix_info = new_interval.fix_information(data, quarter, seuil, delta, interval_flight, interval_data)
        total_fix_list = new_interval.fix_set(total_fix_info, interval_data)
        fix_set = []
        for i in total_fix_list:
            if i[0] in interval_set:
                fix_set.append(interval_set.index(i))  # 找到当前quarter、当前part下后半小时固定的variable
                # print(second_interval_data['begin_interval'][i[0]],
                #       second_interval_data['end_interval'][i[0]],
                #       second_interval_data['registration'][i[0]],
                #       second_interval_data['begin_callsign'][i[0]],
                #       second_interval_data['end_callsign'][i[0]])

        # Gates for fixed intervals
        gate_fix = new_interval.gate_set(total_fix_info, gate_dict)
        print(len(fix_set), 'fix_set', len(gate_fix), 'gate_fix')

        # Check if fixed part has conflicts
        fix_set, gate_fix = find_obstruction(fix_set, obstruction, interval_data, interval_set, quarter, gate_fix)

        # Fix variables in fix_set
        x = variable.actual_x(temp_x, gate_fix, fix_set, gate_set, interval_data, interval_set)  # 更新x

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
        # temp_list = []
        # temp_i1 = []
        # # temp_i2 = []
        # for i in range(len(x)):
        #     if sum(x[i]) == 1:
        #         for temp in range(len(x[i])):
        #             if x[i][temp] == 1:
        #                 temp_list.append(temp)
        #                 temp_i1.append(interval_data['begin_callsign'][interval_set_total[i]])
        #                 # temp_i2.append(interval_data['registration'][interval_set_total[i]])
        #                 print(interval_data['begin_callsign'][interval_set_total[i]], temp)
        # print(len(temp_i1), 'x list', len(temp_list), "x gate")
        # # print(temp_i2, "x list")
        # # print(len(temp_list), "x gate")
        # print(len(interval_set_total))

        # 优化
        # Objective
        target_matrix = matrix.target_re(gate_dict, interval_data, interval_set, gate_set, genernate, taxiingtime,
                                         interval_pattern, wingsize)

        # Optimization
        result = optim_temp.optim(x, obstruction, target_matrix, part)
        status = result[3]
        gate_choose = result[1]

        # Store old solution
        old_gate_dic = gate_dict

        # Get results
        assert status != 3, "the model is infeasible"
        gate_dict = variable.SpecialVariable.get_aim_dict(gate_choose, interval_set, interval_data)

        # if status != 3:
        #     gate_dict = variable.SpecialVariable.get_aim_dict(gate_choose, interval_set, interval_data)

        # if status == 3:
        #     print("the model is infeasible")
        #     sys.exit(1)
        #     t = 30
        #     if_interval = IfInfeasible()
        #     delta_temp = 5
        #     interval = if_interval.presolve(quarter, data, seuil, delta_temp)  # 计算当前quarter下的interval
        #     second_interval_data = interval[0]
        #
        #     # 计算当前quarter下的variable
        #     variable_set = variable.variable(second_interval_data, airline, wingsize, part, interval_flight, data,
        #                                      quarter)
        #     interval_data = variable_set[0]  # 所有interval的数据 每半分钟
        #     interval_set = variable_set[1]
        #     obstruction = variable.get_obstruction(interval_data, interval_set)
        #     temp_x = variable_set[3]
        #     gate_set = variable_set[2]
        #
        #     # 验证interval是否有小于零的情况
        #     for i in range(len(interval_data['interval'])):
        #         if interval_data['interval'][i] < 0:
        #             print(interval_data['registration'][i],
        #                   interval_data['begin_callsign'][i], interval_data['end_callsign'][i], '001')
        #             sys.exit(1)
        #
        #     # 计算当前quarter后半小时？固定的variable
        #     total_fix_info = if_interval.fix_information(data, quarter, seuil, delta_temp,
        #                                                  interval_flight, interval_data, t)
        #     total_fix_list = if_interval.fix_set(total_fix_info, interval_data)
        #     fix_set = []
        #     for i in total_fix_list:
        #         if i in interval_set:
        #             # 找到当前quarter、当前part下后半小时固定的variable fix_set是interval_set中的索引
        #             fix_set.append(interval_set.index(i))
        #     x = variable.actual_x(temp_x, gate_fix, fix_set, gate_set, interval_data, interval_set)  # 更新x
        #     gate_dict = localsearch.local_search(x, obstruction, interval_set, interval_data, fix_set, gate_dict)
        #     # outputdata.write_xls(gate_dict, 'before', gate_set, interval_data, interval_set)
        #     gate_dict = localsearch.remote_allocation(gate_dict, wingsize, gate_set, interval_set, interval_data,
        #                                               obstruction)
        #     outputdata.write_xls(gate_dict, 'after', gate_set, interval_data, interval_set)
        #
        #     # dic = plot.make_json(generation, interval_set, interval_data)
        #     # flag = plot.dict2json('E:/gap/results/python/buffer/j_data.json', dic)
        #     # print(flag)

        # 计数
        counter = change_times(old_gate_dic, gate_dict, counter)
        # process_to_csv.write_process(gate_dict, sheetname, gate_set, regulation, quarter)
        quarter += 1
        print(quarter)

    remote_number = final_remote(gate_dict, airline, interval_data, gate_set)
    # to_csv.write_final(gate_dict, sheetname, gate_set, pattern, regulation, filename, counter, remote_number)
    return gate_dict
