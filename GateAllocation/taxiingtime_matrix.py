from GateAllocation.variable import SpecialVariable


class Matrix:
    @staticmethod
    def taxiingtime_matrix(taxiingtime, interval_data, interval_pattern):
        # The taxiing time for each interval assigned to different gates
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

    def find_used(self, taxiingtime, interval_data, interval_pattern, interval_set, wingsize, gate_set):
        # The required taxi time
        taxi_matrix = self.taxiingtime_matrix(taxiingtime, interval_data, interval_pattern)
        # Build a two-dimensional list of taxiing times for all intervals and all gates.
        target_matrix = [row for i, row in enumerate(taxi_matrix) if i in interval_set]
        gate_index = [index for index, value in enumerate(wingsize.keys()) if value in gate_set]
        # print(gate_index)
        target_matrix = [row[g] for row in target_matrix for g in gate_index]
        target_matrix = [target_matrix[i:i + len(gate_index)] for i in range(0, len(target_matrix), len(gate_index))]
        return target_matrix

    def target_gen(self, wingsize, interval_set, gate_set, part, interval_data, airline, taxiingtime, interval_pattern):
        target_matrix = self.find_used(taxiingtime, interval_data, interval_pattern, interval_set, wingsize, gate_set)

        if part == 3:
            remote_gate = SpecialVariable.remote_gate()
            remote_index = [index for index, value in enumerate(gate_set) if value in remote_gate]

            alpha = 1000 * 1000
            for i in range(len(interval_set)):
                for j in remote_index:
                    target_matrix[i][j] = target_matrix[i][j] + alpha * 10
                # Whether the interval can use remote parking stands
                intersection = list(set(airline[interval_data['airline'][interval_set[i]]]) & set(remote_gate))
                if not intersection:
                    # None of the remote stands could be used
                    continue
                else:
                    # The indices of the remote stands could be used
                    intersection_index = [index for index, value in enumerate(gate_set) if value in intersection]
                    for h in intersection_index:
                        target_matrix[i][h] = target_matrix[i][h] - alpha * 9
        # print(target_matrix[80])
        return target_matrix


class ReMatrix(Matrix):
    @staticmethod
    def last_results(gate_dict, interval_set_total, interval_data):
        # 找到每个interval在上一次计算中的gate 和在interval_set中的索引
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
        return g, interval_index

    def target_re(self, gate_dict, interval_data, interval_set, gate_set, genernate, taxiingtime, interval_pattern,
                  wingsize):
        # TODO:航站楼部分面向“结果”编程
        target_matrix = self.find_used(taxiingtime, interval_data, interval_pattern, interval_set, wingsize, gate_set)
        # index of every interval in interval_set and the gate in last interation
        g, interval_index = self.last_results(gate_dict, interval_set, interval_data)

        # terminal 1 and 2  remote stands
        no_1 = [x for x in range(5)]
        no_2 = [x for x in range(5, 35)]
        no_3 = [x for x in range(35, 46)]
        no_3.extend([x for x in range(56, 68)])
        no_4 = [x for x in range(46, 56)]

        # 构建target_matrix
        n = len(interval_set)
        for i in range(n):
            if i in interval_index:
                # i is element in interval_index
                # interval_index is the list of index of interval_set
                # e.g. interval_set = [3, 4, 7, 8, ...] interval_index = [0, 1, 3, ...]
                # i = 3 interval_index.index(i) = 2
                # interval_set[i] = 8
                if g[interval_index.index(i)] in no_1 + no_2:
                    target_matrix = self.cost_contact(g, i, no_1, no_2, no_3, no_4, target_matrix, interval_index)
                    target_matrix = self.cost_contact(g, i, no_2, no_1, no_3, no_4, target_matrix, interval_index)
                else:
                    initg = self.find_gate(i, genernate, interval_data, interval_set)
                    target_matrix = self.cost_remote(g, initg, interval_index, i, no_1, no_2, no_3, no_4, target_matrix)
                    target_matrix = self.cost_remote(g, initg, interval_index, i, no_1, no_2, no_4, no_3, target_matrix)
            else:
                pass
        return target_matrix

    @staticmethod
    def find_gate(i, genernate, interval_data, interval_set):
        idx = interval_set[i]
        if interval_data['begin_callsign'][idx] in genernate['begin_callsign']:
            temp = [j for j, values in enumerate(genernate['begin_callsign'])
                    if values == interval_data['begin_callsign'][idx]]
            if len(temp) == 1:
                initg = genernate['gate'][temp[0]]
            else:
                value = [values for values in temp
                         if genernate['registration'][values] == interval_data['registration'][idx]]
                initg = genernate['gate'][value[0]]
        else:
            initg = None
        return initg

    @staticmethod
    def cost_contact(g, i, no_1, no_2, no_3, no_4, target_matrix, interval_index):
        if g[interval_index.index(i)] in no_1:
            alpha = 1000 * 1000
            # terminal 1 and 2
            for k in no_1:
                target_matrix[i][k] = alpha * 1 + target_matrix[i][k]
            target_matrix[i][g[interval_index.index(i)]] = - alpha * 1 + target_matrix[i][g[interval_index.index(i)]]
            for k in no_2:
                target_matrix[i][k] = alpha * 10 + target_matrix[i][k]

            # remote stands
            rest = no_3 + no_4
            for k in rest:
                target_matrix[i][k] = alpha * 100 + target_matrix[i][k]
        return target_matrix

    @staticmethod
    def cost_remote(g, initgate, interval_index, i, no_1, no_2, no_3, no_4, target_matrix):
        localgate = g[interval_index.index(i)]
        if localgate in no_3:
            alpha = 1000 * 1000

            if initgate:
                temp = no_1 + no_2
                if initgate in temp:

                    # contact stands
                    for k in temp:
                        target_matrix[i][k] = 0 * alpha + target_matrix[i][k]

                    # remote stands
                    rest = no_3 + no_4
                    for k in rest:
                        target_matrix[i][k] = 10 * alpha + target_matrix[i][k]

                    # the origin stand
                    target_matrix[i][localgate] = - 9 * alpha + target_matrix[i][localgate]
                else:
                    # contact stands
                    for k in temp:
                        target_matrix[i][k] = 1 * alpha + target_matrix[i][k]

                    # remote stands
                    rest = no_3 + no_4
                    for k in rest:
                        target_matrix[i][k] = 10 * alpha + target_matrix[i][k]

                    # the origin stand
                    target_matrix[i][localgate] = - 10 * alpha + target_matrix[i][localgate]
            else:
                # contact stands
                temp = no_1 + no_2
                for k in temp:
                    target_matrix[i][k] = 0 * alpha + target_matrix[i][k]

                # remote stands
                rest = no_3 + no_4
                for k in rest:
                    target_matrix[i][k] = 10 * alpha + target_matrix[i][k]

                # the origin stand
                target_matrix[i][localgate] = - 9 * alpha + target_matrix[i][localgate]
        return target_matrix
