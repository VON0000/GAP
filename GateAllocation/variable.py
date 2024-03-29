import pandas as pd
import numpy as np
import math


class SpecialVariable:
    @staticmethod
    def remote_gate():
        remote_gate = ['409', '410', '411', '412', '413', '414', '415', '416', '417', '418', '419',
                       '414L', '414R', '415L', '415R', '416L', '416R', '417L', '417R', '418L', '418R', '419L', '419R',
                       '601', '602', '603', '604', '605', '606', '607', '608', '609', '610']
        return remote_gate

    @staticmethod
    def get_aim_dict(gate_choose: list, interval_set: list, interval_data: dict):
        temp_1 = []
        temp_2 = []
        temp_3 = []
        temp_4 = []
        temp_5 = []
        temp_6 = []
        for i in range(len(gate_choose)):
            index = interval_set[i]
            temp_1.append(interval_data['begin_callsign'][index])
            temp_2.append(interval_data['registration'][index])
            temp_3.append(gate_choose[i])
            temp_4.append(interval_data['end_callsign'][index])
            temp_5.append(interval_data['begin_interval'][index])
            temp_6.append(interval_data['end_interval'][index])
        my_key = ['begin_callsign', 'registration', 'gate', 'end_callsign']
        default_value = []
        gate_dict = dict.fromkeys(my_key, default_value)
        gate_dict['begin_callsign'] = temp_1
        gate_dict['registration'] = temp_2
        gate_dict['gate'] = temp_3
        gate_dict['end_callsign'] = temp_4
        gate_dict['begin_interval'] = temp_5
        gate_dict['end_interval'] = temp_6
        return gate_dict


def select(wingsize, i, interval_data, interval_set, airline, gate_set):
    index = [interval_set[i]][0]
    wingspan = np.array(list(wingsize.values()))
    wing_limit = np.where(wingspan >= interval_data['wingspan'][index])[0]
    temp = interval_data['airline'][index]
    company_limit = [i for i, item in enumerate(wingsize.keys()) if item in airline[temp]]
    intersection = set(wing_limit) & set(company_limit)
    intersection_gate = [item for i, item in enumerate(wingsize.keys()) if i in intersection]
    # sort
    fit = [j for j, value in enumerate(gate_set) if value in intersection_gate]
    # print(fit)
    return fit


def add_remote(fit, wingsize, i, interval_data, interval_set, airline, gate_set):
    """

    add remote stands to each interval
    """
    index = interval_set[i]
    temp = interval_data['airline'][index]
    airline_gate = airline[temp]
    remote_gate = SpecialVariable.remote_gate()
    augmentation = list(set(remote_gate) - set(airline_gate))
    wingspan = np.array(list(wingsize.values()))
    wing_limit = np.where(wingspan >= interval_data['wingspan'][index])[0]
    aug_limit = [i for i, item in enumerate(wingsize.keys()) if item in augmentation]
    intersection = set(wing_limit) & set(aug_limit)
    intersection_gate = [item for i, item in enumerate(wingsize.keys()) if i in intersection]
    # sort
    fit = fit + [j for j, value in enumerate(gate_set) if value in intersection_gate]
    fit = sorted(fit)
    return fit


def timetransform(second_interval_data):
    """

    second -> half minutes
    """
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
    """

    Airlines with overlapping use of parking stands
    """
    if part == 1:
        data = pd.read_excel("../data/group/firstpart.xlsx", sheet_name=None, header=None)
    elif part == 2:
        data = pd.read_excel("../data/group/secondpart.xlsx", sheet_name=None, header=None)
    elif part == 3:
        data = pd.read_excel("../data/group/thirdpart.xlsx", sheet_name=None, header=None)
    elif part == 4:
        data = pd.read_excel("../data/group/fourthpart.xlsx", sheet_name=None, header=None)
    else:
        data = pd.read_excel("../data/group/fifthpart.xlsx", sheet_name=None, header=None)
    sheet_data = data['Feuil1']
    company_set = sheet_data.iloc[:, 0]
    company_set = company_set.tolist()
    return company_set


def variable(second_interval_data, airline, wingsize, part, interval_flight, data, quarter):
    """

    Get the variables in optimization ,find those variables that should be 0 which means
    the interval can not be allocated to the gate because of the limitation wingspan or airline
    """
    # all interval that satisfy the limit of airlines
    company_set = get_companyset(part)
    temp = np.isin(second_interval_data['airline'], company_set)
    interval_set = list(np.where(temp)[0])

    # delete those target time earlier than current moment and actual time later than current moment + 60 minutes
    departure_set = np.where(np.array(data['departure']) == 'ZBTJ')[0]
    h = 60 * 60
    q = 15 * 60
    n = len(data['data'])
    del_list_data = []
    for i in range(n):
        if i in list(departure_set):
            if data['ATOT'][i] > quarter * q + h and data['TTOT'][i] < quarter * q:
                del_list_data.append(i)
        else:
            if data['ALDT'][i] > quarter * q + h and data['TLDT'][i] < quarter * q:
                del_list_data.append(i)
    # print(del_list_data)
    # print(len(interval_set))
    for i in range(len(interval_flight)):
        inter = list(set(del_list_data) & set(interval_flight[i]))  # Check if this interval should be deleted
        if len(inter) != 0 and i in interval_set:
            if interval_flight[i][0] == inter[0]:
                interval_set.remove(i)
            else:
                second_interval_data['end_interval'][i] = second_interval_data['begin_interval'][i] + 15 * 60
                second_interval_data['interval'][i] = 15 * 60
                second_interval_data['end_callsign'][i] = second_interval_data['begin_callsign'][i]

    #  All gates in use
    gate = list(wingsize.keys())
    gate_set = set().union(*[airline[key] for key in company_set])
    gate_set = sorted(gate_set, key=lambda y: gate.index(y))

    # Verify whether there are intervals that do not satisfy airline and wingspan restrictions for parking stands
    # Obtain x.
    n = len(interval_set)
    m = len(gate_set)
    # print(n, m)
    x = [[0] * m for _ in range(n)]
    del_set = []
    for i in range(n):
        fit = select(wingsize, i, second_interval_data, interval_set, airline, gate_set)
        if part == 3:
            fit = add_remote(fit, wingsize, i, second_interval_data, interval_set, airline, gate_set)
        if len(fit) == 0:
            del_set.append(i)
        for j in fit:
            x[i][j] = 1
    assert len(del_set) == 0, \
        "There are intervals that do not satisfy airline and wingspan restrictions for parking stands"

    # print(interval_set)
    min_interval_data = timetransform(second_interval_data)
    return min_interval_data, interval_set, gate_set, x


# def variable_infeasible(second_interval_data, airline, wingsize, part, quarter, interval_set_total, counter, pr_temp):
#     h = 60 * 60
#     company_set = get_companyset(part)
#     temp = np.isin(second_interval_data['airline'], company_set)
#     temp_set1 = np.where(temp)[0]
#     temp_set2 = np.where(np.array(second_interval_data['begin_interval']) <= quarter * 15 * 60 + h)[0]
#     interval_set = np.intersect1d(temp_set1, temp_set2)
#     interval_set = list(interval_set)
#
#     if counter == 2:
#         for i in pr_temp[1]:
#             pr_temp[0].remove(i)
#         for i in pr_temp[0]:
#             interval_set.remove(i)
#     # temp_set3 = np.where((quarter * 15 * 60 <= np.array(second_interval_data['end_interval'])) &
#     #                      (np.array(second_interval_data['begin_interval']) <= quarter * 15 * 60 + h))[0]
#     # interval_pr = np.intersect1d(temp_set1, temp_set3)
#     # interval_pr = list(interval_pr)
#     # print(len(interval_pr))
#     # for i in range(37):
#     #     interval_set.remove(interval_pr[i])
#     n = len(interval_set)
#     # print(n, "n")
#     gate = list(wingsize.keys())
#     gate_set = set().union(*[airline[key] for key in company_set])
#     gate_set = sorted(gate_set, key=lambda y: gate.index(y))
#     m = len(gate_set)
#     x = [[0] * m for _ in range(n)]
#     del_set = []
#     for i in range(n):
#         fit = select_infeasible(wingsize, i, second_interval_data, interval_set, airline, gate_set, interval_set_total)
#         if len(fit) == 0:
#             del_set.append(i)
#         for j in fit:
#             x[i][j] = 1
#         # if interval_set[i] in interval_pr:
#         #     print(second_interval_data['begin_interval'][interval_set[i]],
#         #           second_interval_data['end_interval'][interval_set[i]],
#         #           second_interval_data['registration'][interval_set[i]],
#         #           second_interval_data['begin_callsign'][interval_set[i]],
#         #           second_interval_data['end_callsign'][interval_set[i]], fit)
#     if len(del_set) != 0:
#         print(del_set, "del_set")
#         sys.exit(1)
#     # print(interval_set)
#     min_interval_data = timetransform(second_interval_data)
#     return min_interval_data, interval_set, gate_set, x
#
#
# def select_infeasible(wingsize, i, interval_data, interval_set, airline, gate_set, interval_set_total):
#     index = np.where(interval_set_total == interval_set[i])[0]
#     index = interval_set_total[index[0]]
#     wing_limit = np.where(list(wingsize.values()) >= interval_data['wingspan'][index])[0]
#     temp = interval_data['airline'][index]
#     company_limit = [i for i, item in enumerate(wingsize.keys()) if item in airline[temp]]
#     intersection = set(wing_limit) & set(company_limit)
#     intersection_gate = [item for i, item in enumerate(wingsize.keys()) if i in intersection]
#     # 排序
#     fit = [j for j, value in enumerate(gate_set) if value in intersection_gate]
#     # print(fit)
#     return fit


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
    """

    conflicts for each interval
    """
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
