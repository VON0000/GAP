import sys
import gurobipy as gp
from gurobipy import GRB
import time
import re


def find_numbers(text):
    # 检查字符串是否包含路径分隔符 "\"
    # check if the string contains path separator "\"
    is_path = "\\" in text

    if is_path:
        found_number = re.findall(r'\d+', text.split('\\')[-1])
    else:
        found_number = re.findall(r'\d+', text)

    return found_number


class Optimization:
    """
    Optimization
    variable: x
    constraints: Every interval has one and only one parking position.
                 Meet the constraints of both the airline and wingspan.
                 Dependent gate e.g. 414R/414 414L/414
    objective: Minimize the number of parking stand changes
               Maximize the utilization of nearby parking stands
               Minimize the sum of taxiing time
    """

    # TODO:改 dependent gate 限制条件
    @staticmethod
    def dependent_gate():
        my_key = ['gate', 'dependent']
        default_value = []
        dependent_dic = dict.fromkeys(my_key, default_value)
        gate = [40, 41, 42, 43, 44, 45, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67]
        dependent = [[56, 57], [58, 59], [60, 61], [62, 63], [64, 65], [66, 67],
                     [40], [40], [41], [41], [42], [42], [43], [43], [44], [44], [45], [45]]
        dependent_dic['gate'] = gate
        dependent_dic['dependent'] = dependent
        return dependent_dic

    @staticmethod
    def dependent_set():
        dependent_set = [40, 41, 42, 43, 44, 45, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67]
        return dependent_set

    @staticmethod
    def part_4(i, j, counter, a, b, model, x):
        model.addConstr(x[i, a] + x[j, b] <= 1, name=" ".join(["constraint", str(counter)]))
        counter += 1
        return model, counter

    def optim(self, y, obstruction, target_matrix, part):
        t1 = time.time()
        model = gp.Model()
        n = len(y)
        m = len(y[0])
        for i in range(n):
            if len(y[i]) == 0:
                print(i, "x error")
                sys.exit(1)
        x = model.addVars(n, m, vtype=GRB.BINARY, name="x")
        counter = 0
        for i in range(n):
            for j in range(m):
                if y[i][j] == 0:
                    model.addConstr(x[i, j] == 0, name=" ".join(["constraint", str(counter)]))
                    counter += 1
        for i in range(n):
            sum_expr = gp.quicksum(x[i, j] for j in range(m))
            model.addConstr(sum_expr == 1, name=" ".join(["constraint", str(counter)]))
            counter += 1
        for k in range(m):
            for i in range(n):
                temp = obstruction[i]
                model.addConstrs((x[i, k] + x[j, k] <= 1 for j in temp), name=" ".join(["constraint", str(counter)]))
                counter += 1
        if part == 3:
            for i in range(n):
                temp = obstruction[i]
                if len(temp) == 0:
                    continue
                else:
                    for j in temp:
                        model.addConstrs((x[i, 40 + g] + x[j, 57 + (g - 1) * 2 + 1] <= 1 for g in range(6)),
                                         name=" ".join(["constraint", str(counter)]))
                        model.addConstrs((x[i, 40 + g] + x[j, 57 + (g - 1) * 2 + 2] <= 1 for g in range(6)),
                                         name=" ".join(["constraint", str(counter + 1)]))
                        counter += 2
        if part == 4:
            for i in range(n):
                temp = obstruction[i]
                if len(temp) == 0:
                    continue
                else:
                    for j in temp:
                        results_set = self.part_4(i, j, counter, 8, 43, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 8, 44, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 9, 45, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 9, 46, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 20, 47, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 20, 48, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 21, 49, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 21, 50, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 31, 51, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 32, 52, model, x)
                        model = results_set[0]
                        counter = results_set[1]
                        results_set = self.part_4(i, j, counter, 33, 53, model, x)
                        model = results_set[0]
                        counter = results_set[1]
        # print(model)
        model = self.objective(x, n, m, target_matrix, model)
        model.optimize()
        status = model.status
        print('优化结束')
        t2 = time.time()
        optim_time = t2 - t1
        print('程序运行时间:%s毫秒' % (optim_time * 1000))
        if status != 3:
            gate_choose = []
            for v in model.getVars():  # getVars获取所有变量
                if v.x == 1:
                    # print("%s %g" % (v.varName, v.x))  # (v.varName,v.x)是（变量名字，优化结果）
                    temp = find_numbers(v.varName)[1]
                    gate_choose.append(int(temp))
            # print(gate_choose)
            # print("Obj: %g" % model.objVal)
            obj = model.objVal
        else:
            # model.computeIIS()
            # model.write("model1.ilp")
            obj = None
            gate_choose = None
            pass
        return optim_time * 1000, gate_choose, obj, status

    @staticmethod
    def objective(x, n, m, target_matrix, model):
        objective_expr = gp.quicksum(target_matrix[i][j] * x[i, j] for i in range(n) for j in range(m))
        model.setObjective(objective_expr, GRB.MINIMIZE)
        return model
