from random import choice
import sys
from optimization import Optimization
import numpy as np
from copy import deepcopy
import plot


def valid_gate(x, n):
    viable_gate = []
    for i in range(n):
        suitable_gate = x[i]
        temp = []
        for j in range(len(suitable_gate)):
            if suitable_gate[j] == 1:
                temp.append(j)
        viable_gate.append(temp)
    # print(viable_gate)
    return viable_gate


def choose_random_valid_gate(i, x, obstruction, viable_gate, dependent_dic, dependent_set):
    local_obstruction = obstruction[i]
    # print(len(interval_set), 'interval_set')
    temp = viable_gate[i]
    possible_gate = []
    for j in temp:
        flight_avant = []  # 在此之前分配到这个gate的interval

        # 有dependent gate
        if j in dependent_set:
            for k in range(len(x)):
                if x[k][j] == 1:
                    flight_avant.append(k)
            idx = np.where(np.array(dependent_dic['gate']) == j)[0][0]
            for jdx in dependent_dic['dependent'][idx]:
                for k in range(len(x)):
                    if x[k][jdx] == 1:
                        flight_avant.append(k)

        # 无dependent gate
        else:
            for k in range(len(x)):
                if x[k][j] == 1:
                    flight_avant.append(k)

        # 判断是否冲突
        flight_obstruction = list(set(flight_avant) & set(local_obstruction))
        if len(flight_obstruction) == 0:
            possible_gate.append(j)
    if len(possible_gate) == 0:
        g = -1
    else:
        g = choice(possible_gate)
    return g


def force_attribution(q, gen_x, i, viable_gate, obstruction, fix_set, dependent_dic, dependent_set):
    m = len(gen_x[0])
    local_obstruction = obstruction[i]
    temp = viable_gate[i]
    flag = 0
    while len(temp) != 0:
        g = choice(temp)
        flight_avant = []

        # 有dependent gate
        if g in dependent_set:
            for k in range(len(gen_x)):
                if gen_x[k][g] == 1:
                    flight_avant.append(k)
            idx = np.where(np.array(dependent_dic['gate']) == g)[0][0]
            for jdx in dependent_dic['dependent'][idx]:
                for k in range(len(gen_x)):
                    if gen_x[k][jdx] == 1:
                        flight_avant.append(k)

        # 无dependent gate
        else:
            for j in range(len(gen_x)):
                if gen_x[j][g] == 1:
                    flight_avant.append(j)

        # 判断是否冲突
        flight_obstruction = list(set(flight_avant) & set(local_obstruction))
        judge = list(set(flight_obstruction) & set(fix_set))
        if len(judge) == 0:
            flag = 0
            q = flight_obstruction + q
            gen_x[i][g] = 1
            for j in flight_obstruction:
                gen_x[j] = [0] * m
            break
        else:
            temp.remove(g)

    if len(temp) == 0:
        flag = 1
    return q, gen_x, flag


def generate_feasible_solution(x, obstruction, interval_set, interval_data, fix_set):
    # 初始化和边界条件
    k = 50
    q = [x for x in range(len(interval_set))]
    flight_after_problem = -1
    counter = 0
    n = len(x)
    m = len(x[0])
    gen_x = [[0] * m for _ in range(n)]

    optim_temp = Optimization()
    dependent_dic = optim_temp.dependent_gate()
    dependent_set = optim_temp.dependent_set()

    # 将fix_set固定 同时验证fix_set是否只有一个gate
    for i in fix_set:
        w = []
        for j in range(len(x[i])):
            if x[i][j] == 1:
                w.append(j)
        if len(w) == 1:
            gen_x[i][w[0]] = 1
            q.remove(i)
        else:
            print('fix_set error')
            sys.exit(1)

    viable_gate = valid_gate(x, n)
    infeasible = []  # 在interval_set中的索引
    while len(q) != 0:
        i = q[0]
        q.pop(0)
        if flight_after_problem == i:
            flight_after_problem = -1
            counter = 0
        g = choose_random_valid_gate(i, gen_x, obstruction, viable_gate, dependent_dic, dependent_set)
        if g != -1:
            gen_x[i][g] = 1
        else:
            counter = counter + 1
            if counter < k:
                if flight_after_problem == -1:
                    flight_after_problem = q[0]
                results = force_attribution(q, gen_x, i, viable_gate, obstruction, fix_set,
                                            dependent_dic, dependent_set)
                flag = results[2]
                if flag == 0:
                    q = results[0]
                    gen_x = results[1]
                else:
                    infeasible.append(i)
                    counter = 0
                    continue
            else:
                infeasible.append(i)
                counter = 0
                continue
    for i in infeasible:
        print(interval_data['begin_callsign'][interval_set[i]], 'INFEASIBLE')
    l_temp = list(set(infeasible) & set(fix_set))
    if len(l_temp) != 0:
        for i in l_temp:
            print(interval_data['begin_callsign'][interval_set[i]], "error")
    # for i in range(len(gen_x)):
    #     for j in range(len(gen_x[i])):
    #         if gen_x[i][j] == 1:
    #             print(i, j)
    #     print('/')
    gate_dict = make_dict(gen_x, interval_data, interval_set, infeasible)
    return gate_dict, gen_x, infeasible


def make_dict(gen_x, interval_data, interval_set, infeasible):
    temp_1 = []
    temp_2 = []
    temp_3 = []
    temp_4 = []
    for i in range(len(gen_x)):
        index = interval_set[i]
        temp_1.append(interval_data['begin_callsign'][index])
        temp_2.append(interval_data['registration'][index])
        temp_4.append(interval_data['end_callsign'][index])
        if sum(gen_x[i]) == 1:
            for j in range(len(gen_x[i])):
                if gen_x[i][j] == 1:
                    temp_3.append(j)
        else:
            if i not in infeasible:
                print("infeasible error", infeasible, "solution")
                sys.exit(1)
            temp_3.append([])
    my_key = ['begin_callsign', 'registration', 'gate', 'end_callsign']
    default_value = []
    gate_dict = dict.fromkeys(my_key, default_value)
    gate_dict['begin_callsign'] = temp_1
    gate_dict['registration'] = temp_2
    gate_dict['gate'] = temp_3
    gate_dict['end_callsign'] = temp_4
    return gate_dict


def cal_fitness(origin_dict, gate_dict):
    # 初始化
    n = len(gate_dict['gate'])
    fitness = 0

    for i in range(n):
        # 得到之前的gate
        begin_callsign = gate_dict['begin_callsign'][i]
        registration = gate_dict['registration'][i]
        gate = gate_dict['gate'][i]
        temp_1 = [j for j, value in enumerate(origin_dict['begin_callsign']) if value == begin_callsign]
        temp_2 = [j for j, value in enumerate(origin_dict['registration']) if value == registration]
        idx = list(set(temp_1) & set(temp_2))
        if len(idx) != 1 and len(idx) != 0:
            print('idx error')
            sys.exit(1)
        else:
            if len(idx) == 1:
                idx = idx[0]
                origin_gate = origin_dict['gate'][idx]
            else:
                origin_gate = []

        # 航站楼一号、二号、远机位
        no_1 = [x for x in range(5)]
        no_2 = [x for x in range(5, 35)]
        no_3 = [x for x in range(35, 46)]
        no_3.extend([x for x in range(56, 68)])
        no_4 = [x for x in range(46, 56)]

        if not origin_gate:
            fitness = fitness + 0
        elif origin_gate in no_1:
            fitness = judgment(gate, no_1, fitness)
        elif origin_gate in no_2:
            fitness = judgment(gate, no_2, fitness)
        elif origin_gate in no_3:
            fitness = judgment(gate, no_3, fitness)
        else:
            fitness = judgment(gate, no_4, fitness)
    return fitness


def judgment(gate, no, fitness):
    if gate in no:
        fitness = fitness + 1
    elif not gate:
        fitness = fitness + 100
    else:
        fitness = fitness + 10
    return fitness


def swap(solution, x, obstruction, infeasible):
    # 初始化
    n = len(x)
    viable_gate = valid_gate(x, n)
    optim_temp = Optimization()
    dependent_dic = optim_temp.dependent_gate()
    dependent_set = optim_temp.dependent_set()

    # 随机选择一个航班
    temp = [x for x in range(n)]
    s1 = []
    while temp:
        s1 = choice(temp)
        if s1 in infeasible:
            temp.remove(s1)
        else:
            break
    old_gate = np.where(np.array(solution[s1]) == 1)[0][0]
    available_gate = viable_gate[s1]
    available_gate.remove(old_gate)
    s2 = s1

    j = old_gate
    while len(available_gate) != 0:
        j = choice(available_gate)
        results = judge_exist_flight(j, dependent_set, dependent_dic, solution, obstruction, s1)
        exist_local = results[0]
        judge_local = results[1]
        judge_neighbor = results[2]
        if len(judge_neighbor) == 0:
            if len(judge_local) == 0:
                available_flight = exist_local
            elif len(judge_local) == 1:
                available_flight = judge_local
            else:
                available_gate.remove(j)
                continue
        else:
            available_gate.remove(j)
            continue
        s2 = reverse(available_flight, old_gate, viable_gate, obstruction, solution, s1, dependent_set, dependent_dic)

        if s2 != s1:
            break
        else:
            available_gate.remove(j)
    temp = solution[s1]
    solution[s1] = solution[s2]
    solution[s2] = temp
    solution = input_infeasible(solution, viable_gate, old_gate, j, infeasible, obstruction)
    return solution


def input_infeasible(solution, viable_gate, old_gate, j, infeasible, obstruction):
    for i in infeasible:
        if sum(solution[i]) != 0:
            print("infeasible error input_infeasible")
            sys.exit(1)
        exist_flight = []
        if j != old_gate:
            if j in viable_gate[i]:
                for k in range(len(solution)):
                    if solution[k][j] == 1:
                        exist_flight.append(k)
                temp = list(set(exist_flight) & set(obstruction[i]))
                if len(temp) == 0:
                    solution[i][j] = 1
                    infeasible.remove(i)
            elif old_gate in viable_gate[i]:
                for k in range(len(solution)):
                    if solution[k][old_gate] == 1:
                        exist_flight.append(k)
                temp = list(set(exist_flight) & set(obstruction[i]))
                if len(temp) == 0:
                    solution[i][old_gate] = 1
                    infeasible.remove(i)
            else:
                pass
        else:
            if j in viable_gate[i]:
                for k in range(len(solution)):
                    if solution[k][j] == 1:
                        exist_flight.append(k)
                temp = list(set(exist_flight) & set(obstruction[i]))
                if len(temp) == 0:
                    solution[i][j] = 1
                    infeasible.remove(i)
            else:
                pass
    return solution


def reverse(available_flight, old_gate, viable_gate, obstruction, solution, s1, dependent_set, dependent_dic):
    new_solution = deepcopy(solution)
    new_solution[s1][old_gate] = 0
    s2 = s1
    while len(available_flight) != 0:
        s = choice(available_flight)
        available_gate = viable_gate[s]
        if old_gate in available_gate:
            results = judge_exist_flight(old_gate, dependent_set, dependent_dic, new_solution, obstruction, s)
            judge_local = results[1]
            judge_neighbor = results[2]
            if len(judge_neighbor) == 0:
                if len(judge_local) == 0:
                    s2 = s
                    break
                else:
                    available_flight.remove(s)
                    continue
            else:
                available_flight.remove(s)
                continue
        else:
            available_flight.remove(s)
            continue
    return s2


def judge_exist_flight(j, dependent_set, dependent_dic, solution, obstruction, s1):
    if j not in dependent_set:
        exist_neighbor = []
    else:
        number = np.where(np.array(dependent_set) == j)[0]
        number = number[0]
        dependent = dependent_dic['dependent'][number]
        exist_neighbor = []
        for k in dependent:
            for i in range(len(solution)):
                if solution[i][k] == 1:
                    exist_neighbor.append(i)
    exist_local = []
    for i in range(len(solution)):
        if solution[i][j] == 1:
            exist_local.append(i)
    judge_local = list(set(exist_local) & set(obstruction[s1]))
    judge_neighbor = list(set(exist_neighbor) & set(obstruction[s1]))
    return exist_local, judge_local, judge_neighbor


def change(solution, x, obstruction, infeasible):
    if len(infeasible) > 1:
        n = len(x)
        viable_gate = valid_gate(x, n)
        gate_list = []
        for i in infeasible:
            gate_list.extend(viable_gate[i])
        exist_flight = []
        for k in gate_list:
            for i in range(len(solution)):
                if solution[i][k] == 1:
                    exist_flight.append(i)
        s1 = choice(exist_flight)
        old_gate = np.where(np.array(solution[s1]) == 1)[0][0]
        solution[s1][old_gate] = 0
        solution = input_infeasible(solution, viable_gate, old_gate, old_gate, infeasible, obstruction)
        infeasible.append(s1)
    else:
        pass
    return solution


def local_search(x, obstruction, interval_set, interval_data, fix_set, gate_dict):
    origin_dict = gate_dict
    results_1 = generate_feasible_solution(x, obstruction, interval_set, interval_data, fix_set)
    gate_dict = results_1[0]
    solution = results_1[1]
    infeasible = results_1[2]
    counter = 0
    while counter <= 1000:
        if not infeasible:
            print('infeasible list is empty')
            my_dict = plot.make_json(solution, interval_set, interval_data)
            plot.dict2json('A', my_dict)
            break
        fitvalue = cal_fitness(origin_dict, gate_dict)
        origin_dict = gate_dict
        solution = swap(solution, x, obstruction, infeasible)
        solution = change(solution, x, obstruction, infeasible)
        new_gate_dict = make_dict(solution, interval_data, interval_set, infeasible)
        new_fitvalue = cal_fitness(origin_dict, new_gate_dict)
        if new_fitvalue > fitvalue:
            counter = counter + 1
        else:
            gate_dict = new_gate_dict
    return gate_dict


def remote_allocation(gate_dict, wingsize, gate_set, interval_set, interval_data, obstruction):
    remote = [x for x in range(35, 68)]
    remote_size = []
    for r in remote:
        temp = gate_set[r]
        remote_size.append(wingsize[temp])
    for gate in gate_dict['gate']:
        if not gate:
            idx = gate_dict['gate'].index(gate)
            wingspan = interval_data['wingspan'][interval_set[idx]]
            suitable_gate = list(np.where(np.array(remote_size) >= wingspan)[0])
            while len(suitable_gate) != 0:
                k = choice(suitable_gate)
                exist_flight = [j for j, value in enumerate(gate_dict['gate']) if value == k]
                local_obstruction = obstruction[idx]
                intersection = list(set(exist_flight) & set(local_obstruction))
                if len(intersection) == 0:
                    gate_dict['gate'][idx] = k
                    break
                else:
                    suitable_gate.remove(k)
        else:
            continue
    return gate_dict
