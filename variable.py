import pandas as pd
import numpy as np
import sys
import math


def select(wingsize, i, interval_data, interval_set, airline, gate_set):
    index = [interval_set[i]][0]
    wingspan = np.array(list(wingsize.values()))
    wing_limit = np.where(wingspan >= interval_data['wingspan'][index])[0]
    temp = interval_data['airline'][index]
    company_limit = [i for i, item in enumerate(wingsize.keys()) if item in airline[temp]]
    intersection = set(wing_limit) & set(company_limit)
    intersection_gate = [item for i, item in enumerate(wingsize.keys()) if i in intersection]
    # 排序
    fit = [j for j, value in enumerate(gate_set) if value in intersection_gate]
    # print(fit)
    return fit


def timetransform(second_interval_data):
    my_key = ['interval', 'begin_interval', 'end_interval', 'airline', 'registration', 'begin_callsign',
              'end_callsign', 'wingspan']
    default_value = []
    interval_data = dict.fromkeys(my_key, default_value)
    interval_data['airline'] = second_interval_data['airline']
    interval_data['interval'] = second_interval_data['interval']
    interval_data['registration'] = second_interval_data['registration']
    interval_data['begin_callsign'] = second_interval_data['begin_callsign']
    interval_data['end_callsign'] = second_interval_data['end_callsign']
    interval_data['wingspan'] = second_interval_data['wingspan']
    interval_data['interval'] = [math.ceil(item / 30) for item in second_interval_data['interval']]
    interval_data['begin_interval'] = [math.ceil(item / 30) for item in second_interval_data['begin_interval']]
    interval_data['end_interval'] = [math.ceil(item / 30) for item in second_interval_data['end_interval']]
    return interval_data


def get_companyset(part):
    if part == 1:
        data = pd.read_excel("./data/group/firstpart.xlsx", sheet_name=None, header=None)
    elif part == 2:
        data = pd.read_excel("./data/group/secondpart.xlsx", sheet_name=None, header=None)
    elif part == 3:
        data = pd.read_excel("./data/group/thirdpart.xlsx", sheet_name=None, header=None)
    elif part == 4:
        data = pd.read_excel("./data/group/fourthpart.xlsx", sheet_name=None, header=None)
    else:
        data = pd.read_excel("./data/group/fifthpart.xlsx", sheet_name=None, header=None)
    sheet_data = data['Feuil1']
    company_set = sheet_data.iloc[:, 0]
    company_set = company_set.tolist()
    return company_set


def variable(second_interval_data, airline, wingsize, part, interval_flight, data, quarter):
    # 找到满足航空公司限制的interval
    company_set = get_companyset(part)
    temp = np.isin(second_interval_data['airline'], company_set)
    interval_set = list(np.where(temp)[0])

    # target time 小于当前时间 且 actual time 大于当前时间后一小时 的删除
    departure_set = np.where(np.array(data['departure']) == 'ZBTJ')[0]
    h = 60 * 60
    q = 15 * 60
    n = len(data['data'])
    del_list_data = []
    for i in range(n):
        if i in departure_set:
            if data['ATOT'][i] > quarter * q + h and data['TTOT'][i] < quarter * q:
                del_list_data.append(i)
        else:
            if data['ALDT'][i] > quarter * q + h and data['TLDT'][i] < quarter * q:
                del_list_data.append(i)
    # print(del_list_data)
    # print(len(interval_set))
    for i in range(len(interval_flight)):
        inter = list(set(del_list_data) & set(interval_flight[i]))  # 判断此间隔是否需要删除
        if len(inter) != 0 and i in interval_set:
            interval_set.remove(i)

    # 找到此次计算所用的所有gate
    gate = list(wingsize.keys())
    gate_set = set().union(*[airline[key] for key in company_set])
    gate_set = sorted(gate_set, key=lambda y: gate.index(y))

    # 验证是否有interval无可满足航司及翼展限制的机坪 同时得到x
    n = len(interval_set)
    m = len(gate_set)
    # print(n, m)
    x = [[0] * m for _ in range(n)]
    del_set = []
    for i in range(n):
        fit = select(wingsize, i, second_interval_data, interval_set, airline, gate_set)
        if len(fit) == 0:
            del_set.append(i)
        for j in fit:
            x[i][j] = 1
    # print(del_set, 'del_Set')
    if len(del_set) != 0:
        print(del_set, 'del_Set')
        sys.exit(1)

    # print(interval_set)
    min_interval_data = timetransform(second_interval_data)
    return min_interval_data, interval_set, gate_set, x


def variable_infeasible(second_interval_data, airline, wingsize, part, quarter, interval_set_total, counter, pr_temp):
    h = 60 * 60
    company_set = get_companyset(part)
    temp = np.isin(second_interval_data['airline'], company_set)
    temp_set1 = np.where(temp)[0]
    temp_set2 = np.where(np.array(second_interval_data['begin_interval']) <= quarter * 15 * 60 + h)[0]
    interval_set = np.intersect1d(temp_set1, temp_set2)
    interval_set = list(interval_set)

    if counter == 2:
        for i in pr_temp[1]:
            pr_temp[0].remove(i)
        for i in pr_temp[0]:
            interval_set.remove(i)
    # temp_set3 = np.where((quarter * 15 * 60 <= np.array(second_interval_data['end_interval'])) &
    #                      (np.array(second_interval_data['begin_interval']) <= quarter * 15 * 60 + h))[0]
    # interval_pr = np.intersect1d(temp_set1, temp_set3)
    # interval_pr = list(interval_pr)
    # print(len(interval_pr))
    # for i in range(37):
    #     interval_set.remove(interval_pr[i])
    n = len(interval_set)
    # print(n, "n")
    gate = list(wingsize.keys())
    gate_set = set().union(*[airline[key] for key in company_set])
    gate_set = sorted(gate_set, key=lambda y: gate.index(y))
    m = len(gate_set)
    x = [[0] * m for _ in range(n)]
    del_set = []
    for i in range(n):
        fit = select_infeasible(wingsize, i, second_interval_data, interval_set, airline, gate_set, interval_set_total)
        if len(fit) == 0:
            del_set.append(i)
        for j in fit:
            x[i][j] = 1
        # if interval_set[i] in interval_pr:
        #     print(second_interval_data['begin_interval'][interval_set[i]],
        #           second_interval_data['end_interval'][interval_set[i]],
        #           second_interval_data['registration'][interval_set[i]],
        #           second_interval_data['begin_callsign'][interval_set[i]],
        #           second_interval_data['end_callsign'][interval_set[i]], fit)
    if len(del_set) != 0:
        print(del_set, "del_set")
        sys.exit(1)
    # print(interval_set)
    min_interval_data = timetransform(second_interval_data)
    return min_interval_data, interval_set, gate_set, x


def select_infeasible(wingsize, i, interval_data, interval_set, airline, gate_set, interval_set_total):
    index = np.where(interval_set_total == interval_set[i])[0]
    index = interval_set_total[index[0]]
    wing_limit = np.where(list(wingsize.values()) >= interval_data['wingspan'][index])[0]
    temp = interval_data['airline'][index]
    company_limit = [i for i, item in enumerate(wingsize.keys()) if item in airline[temp]]
    intersection = set(wing_limit) & set(company_limit)
    intersection_gate = [item for i, item in enumerate(wingsize.keys()) if i in intersection]
    # 排序
    fit = [j for j, value in enumerate(gate_set) if value in intersection_gate]
    # print(fit)
    return fit


def actual_x(x, gate_fix, fix_set, gate_set, interval_data, interval_set):
    # temp = []
    m = len(gate_set)
    # print(m, 'gate set')
    for i in range(len(fix_set)):
        x[fix_set[i]] = [0] * m
        x[fix_set[i]][gate_fix[i]] = 1
        # temp.append(interval_data['registration'][interval_set[fix_set[i]]])
    # print(fix_set)
    # print(temp)
    return x


def get_obstruction(interval_data, interval_set):
    n = len(interval_set)
    obstruction = []
    fa = [value for i, value in enumerate(interval_data['begin_interval']) if i in interval_set]
    fd = [value for i, value in enumerate(interval_data['end_interval']) if i in interval_set]
    fa = np.array(fa)
    fd = np.array(fd)
    for i in range(n):
        part1 = np.where((fa[i] <= fd) & (fd <= fd[i]) | (fa[i] <= fa) & (fa <= fd[i]))[0]
        part3 = np.where((fa <= fa[i]) & (fd[i] <= fd))[0]
        obs_list = np.union1d(part1, part3)
        obs_list = list(obs_list)
        obs_list.remove(i)
        obstruction.append(obs_list)
    # print(obstruction)
    return obstruction


def target_gen(taxi_matrix, wingsize, interval_set, gate_set):
    target_matrix = [row for i, row in enumerate(taxi_matrix) if i in interval_set]
    gate_index = [index for index, value in enumerate(wingsize.keys()) if value in gate_set]
    # print(gate_index)
    target_matrix = [row[g] for row in target_matrix for g in gate_index]
    target_matrix = [target_matrix[i:i + len(gate_index)] for i in range(0, len(target_matrix), len(gate_index))]
    # print(target_matrix[80])
    return target_matrix


def target_re(gate_dict, interval_set_total, interval_data, gate_set):
    # 找到每个interval在上一次计算中的gate
    interval_index = []
    g = []
    for i in interval_set_total:
        if interval_data['begin_callsign'][i] in gate_dict['begin_callsign']:
            temp = [j for j, values in enumerate(gate_dict['begin_callsign'])
                    if values == interval_data['begin_callsign'][i]]
            if len(temp) == 1:
                interval_index.append(interval_set_total.index(i))
                g.append(gate_dict['gate'][temp[0]])
            else:
                value = [values for values in temp
                         if gate_dict['registration'][values] == interval_data['registration'][i]]
                interval_index.append(interval_set_total.index(i))
                # print(value)
                g.append(gate_dict['gate'][value[0]])
        else:
            pass

    # 航站楼一号、二号、远机位
    no_1 = [x for x in range(5)]
    no_2 = [x for x in range(5, 35)]
    no_3 = [x for x in range(35, 46)]
    no_3.extend([x for x in range(56, 68)])
    no_4 = [x for x in range(46, 56)]

    # 构建target_matrix
    n = len(interval_set_total)
    m = len(gate_set)
    target_matrix = [[100] * m for _ in range(n)]
    for i in range(m):
        if i in interval_index:
            target_matrix = cost(g, i, no_1, target_matrix)
            target_matrix = cost(g, i, no_2, target_matrix)
            target_matrix = cost(g, i, no_3, target_matrix)
            target_matrix = cost(g, i, no_4, target_matrix)
        else:
            pass
    return target_matrix


def cost(g, i, no, target_matrix):
    if g[i] in no:
        for k in no:
            target_matrix[i][k] = 1
        target_matrix[i][g[i]] = 0
    return target_matrix
