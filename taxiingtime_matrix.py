
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


def target_gen(taxi_matrix, wingsize, interval_set, gate_set):
    target_matrix = [row for i, row in enumerate(taxi_matrix) if i in interval_set]
    gate_index = [index for index, value in enumerate(wingsize.keys()) if value in gate_set]
    # print(gate_index)
    target_matrix = [row[g] for row in target_matrix for g in gate_index]
    target_matrix = [target_matrix[i:i + len(gate_index)] for i in range(0, len(target_matrix), len(gate_index))]
    # print(target_matrix[80])
    return target_matrix


def target_re(gate_dict, interval_set_total, interval_data, gate_set):
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