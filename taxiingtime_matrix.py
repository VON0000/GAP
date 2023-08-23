from variable import SpecialVariable


def taxiingtime_matrix(taxiingtime, interval_data, interval_pattern):
    n = len(interval_data['interval'])
    m = len(taxiingtime.keys())
    gate = list(taxiingtime.keys())
    # print(gate)
    matrix = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            if interval_pattern[i][0] == 0:
                matrix[i][j] = matrix[i][j] + 0
            else:
                matrix[i][j] = matrix[i][j] + taxiingtime[gate[j]][interval_pattern[i][0] - 1]
            if interval_pattern[i][1] == 0:
                matrix[i][j] = matrix[i][j] + 0
            else:
                matrix[i][j] = matrix[i][j] + taxiingtime[gate[j]][interval_pattern[i][1] - 1]
    return matrix


def target_gen(taxi_matrix, wingsize, interval_set, gate_set, part, interval_data, airline):
    target_matrix = [row for i, row in enumerate(taxi_matrix) if i in interval_set]
    gate_index = [index for index, value in enumerate(wingsize.keys()) if value in gate_set]
    # print(gate_index)
    target_matrix = [row[g] for row in target_matrix for g in gate_index]
    target_matrix = [target_matrix[i:i + len(gate_index)] for i in range(0, len(target_matrix), len(gate_index))]
    if part == 3:
        remote_gate = SpecialVariable.remote_gate()
        remote_index = [index for index, value in enumerate(gate_set) if value in remote_gate]
        for i in range(len(interval_set)):
            for j in remote_index:
                target_matrix[i][j] = target_matrix[i][j] + 2000
            intersection = list(set(airline[interval_data['airline'][interval_set[i]]]) & set(remote_gate))
            if not intersection:
                continue
            else:
                intersection_index = [index for index, value in enumerate(gate_set) if value in intersection]
                for h in intersection_index:
                    target_matrix[i][h] = target_matrix[i][h] - 1000
    # print(target_matrix[80])
    return target_matrix


def target_re(gate_dict, interval_set_total, interval_data, interval_set, gate_set, airline):
    # TODO:航站楼部分面向“结果”编程
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
    target_matrix = [[0] * m for _ in range(n)]
    for i in range(n):
        if i in interval_index:
            idx = interval_index.index(i)
            target_matrix = cost_contact(g, idx, no_1, no_2, no_3, no_4, target_matrix,
                                         interval_data, interval_set, airline, gate_set)
            target_matrix = cost_contact(g, idx, no_2, no_1, no_3, no_4, target_matrix,
                                         interval_data, interval_set, airline, gate_set)
            target_matrix = cost_remote(g, idx, no_1, no_2, no_3, no_4, target_matrix,
                                        interval_data, interval_set, airline, gate_set)
            target_matrix = cost_remote(g, idx, no_1, no_2, no_4, no_3, target_matrix,
                                        interval_data, interval_set, airline, gate_set)
        else:
            pass
    return target_matrix


def cost_contact(g, i, no_1, no_2, no_3, no_4, target_matrix, interval_data, interval_set, airline, gate_set):
    if g[i] in no_1:
        # 一号航站楼 二号航站楼
        for k in no_1:
            target_matrix[i][k] = 1
        target_matrix[i][g[i]] = 0
        for k in no_2:
            target_matrix[i][k] = 100

        # 航司机位
        index = interval_set[i]
        company = interval_data['airline'][index]
        company_gate = airline[company]
        company_gate = [i for i, x in enumerate(gate_set) if x in company_gate]

        # 远机位
        rest = no_3 + no_4
        intersection = list(set(rest) & set(company_gate))
        if not intersection:
            for k in rest:
                target_matrix[i][k] = 1000
        else:
            for k in intersection:
                target_matrix[i][k] = 100
            rest = [x for x in rest if x not in intersection]
            for k in rest:
                target_matrix[i][k] = 1000
    return target_matrix


def cost_remote(g, i, no_1, no_2, no_3, no_4, target_matrix, interval_data, interval_set, airline, gate_set):
    if g[i] in no_3:
        # 航司机位
        index = interval_set[i]
        company = interval_data['airline'][index]
        company_gate = airline[company]
        company_gate = [i for i, x in enumerate(gate_set) if x in company_gate]

        if g[i] not in company_gate:
            # 近机位
            temp = no_1 + no_2
            for k in temp:
                target_matrix[i][k] = 0

            # 远机位
            rest = no_3 + no_4
            intersection = list(set(rest) & set(company_gate))
            if not intersection:
                for k in rest:
                    target_matrix[i][k] = 1000 + 1
            else:
                for k in intersection:
                    target_matrix[i][k] = 1
                rest = [x for x in rest if x not in intersection]
                for k in rest:
                    target_matrix[i][k] = 1000 + 1

            # 本机位
            target_matrix[i][g[i]] = 1000
        else:
            # 近机位
            temp = no_1 + no_2
            for k in temp:
                target_matrix[i][k] = 100

            # 远机位
            rest = no_3 + no_4
            intersection = list(set(rest) & set(company_gate))
            for k in intersection:
                target_matrix[i][k] = 1
            rest = [x for x in rest if x not in intersection]
            for k in rest:
                target_matrix[i][k] = 1000 + 1

            # 本机位
            target_matrix[i][g[i]] = 0
    return target_matrix
