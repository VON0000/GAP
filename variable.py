import pandas as pd
import numpy as np
import sys


def select(wingsize, i, interval_data, interval_set, airline, gate_set):
    index = [interval_set[i]][0]
    wing_limit = np.where(list(wingsize.values()) >= interval_data['wingspan'][index])[0]
    temp = interval_data['airline'][index]
    company_limit = [i for i, item in enumerate(wingsize.keys()) if item in airline[temp]]
    intersection = set(wing_limit) & set(company_limit)
    intersection_gate = [item for i, item in enumerate(wingsize.keys()) if i in intersection]
    # 排序
    fit = [j for j, value in enumerate(gate_set) if value in intersection_gate]
    # print(fit)
    return fit


def timetransform(interval_data):
    interval_data['begin_interval'] = [item / 30 for item in interval_data['begin_interval']]
    interval_data['end_interval'] = [item / 30 for item in interval_data['end_interval']]
    return interval_data


def get_companyset(part):
    if part == 1:
        data = pd.read_excel("E:/gap/New Folder/group/firstpart.xlsx", sheet_name=None, header=None)
    elif part == 2:
        data = pd.read_excel("E:/gap/New Folder/group/secondpart.xlsx", sheet_name=None, header=None)
    elif part == 3:
        data = pd.read_excel("E:/gap/New Folder/group/thirdpart.xlsx", sheet_name=None, header=None)
    elif part == 4:
        data = pd.read_excel("E:/gap/New Folder/group/fourthpart.xlsx", sheet_name=None, header=None)
    else:
        data = pd.read_excel("E:/gap/New Folder/group/fifthpart.xlsx", sheet_name=None, header=None)
    sheet_data = data['Feuil1']
    company_set = sheet_data.iloc[:, 0]
    company_set = company_set.tolist()
    return company_set


def variable(interval_data, airline, wingsize, part):
    company_set = get_companyset(part)
    temp = np.isin(interval_data['airline'], company_set)
    interval_set = list(np.where(temp)[0])
    n = len(interval_set)
    gate = list(wingsize.keys())
    gate_set = set().union(*[airline[key] for key in company_set])
    gate_set = sorted(gate_set, key=lambda y: gate.index(y))
    m = len(gate_set)
    x = [[0] * m for _ in range(n)]
    del_set = []
    for i in range(n):
        fit = select(wingsize, i, interval_data, interval_set, airline, gate_set)
        if len(fit) == 0:
            del_set.append(i)
        for j in fit:
            x[i][j] = 1
    print(del_set, 'del_Set')
    if len(del_set) != 0:
        sys.exit(1)
    # print(interval_set)
    interval_data = timetransform(interval_data)
    return interval_data, interval_set, gate_set, x


def actual_x(x, gate_fix, fix_set, gate_set):
    m = len(gate_set)
    for i in range(len(fix_set)):
        x[fix_set[i]] = [0] * m
        x[fix_set[i]][gate_fix[i]] = 1
    return x


def get_obstruction(interval_data, airline, wingsize, part):
    result_set = variable(interval_data, airline, wingsize, part)
    interval_data = result_set[0]
    interval_set = result_set[1]
    n = len(interval_set)
    obstruction = []
    fa = [value for i, value in enumerate(interval_data['begin_interval']) if i in interval_set]
    fd = [value for i, value in enumerate(interval_data['end_interval']) if i in interval_set]
    for i in range(n):
        part1 = np.where((fa[i] <= fd) & (fd <= fd[i]) | (fa[i] <= fa) & (fa <= fd[i]))[0]
        part3 = np.where((fa <= fa[i]) & (fd[i] <= fd))[0]
        obs_list = np.union1d(part1, part3)
        obs_list = list(obs_list)
        obs_list.remove(i)
        obstruction.append(obs_list)
    return obstruction


def target(taxi_matrix, interval_data, airline, wingsize, part):
    result_set = variable(interval_data, airline, wingsize, part)
    interval_set = result_set[1]
    gate_set = result_set[2]
    target_matrix = [row for i, row in enumerate(taxi_matrix) if i in interval_set]
    gate_index = [index for index, value in enumerate(wingsize.keys()) if value in gate_set]
    # print(gate_index)
    target_matrix = [row[g] for row in target_matrix for g in gate_index]
    target_matrix = [target_matrix[i:i + len(gate_index)] for i in range(0, len(target_matrix), len(gate_index))]
    # print(target_matrix[80])
    return target_matrix
