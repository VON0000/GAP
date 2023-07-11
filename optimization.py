import sys
import gurobipy as gp
from gurobipy import GRB
import time
import re


class Optimization:
    @staticmethod
    def find_numbers(text):
        numbers = re.findall(r'\d+', text)
        return numbers

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
                                         name=" ".join(["constraint", str(counter+1)]))
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
        # model.computeIIS()
        # model.write("model1.ilp")
        print('优化结束')
        t2 = time.time()
        gate_choose = []
        for v in model.getVars():  # getVars获取所有变量
            if v.x == 1:
                # print("%s %g" % (v.varName, v.x))  # (v.varName,v.x)是（变量名字，优化结果）
                temp = self.find_numbers(v.varName)[1]
                gate_choose.append(int(temp))
        # print(gate_choose)
        # print("Obj: %g" % model.objVal)
        obj = model.objVal
        optim_time = t2 - t1
        print('程序运行时间:%s毫秒' % (optim_time*1000))
        # print(gate_choose)
        return optim_time*1000, gate_choose, obj

    @staticmethod
    def objective(x, n, m, target_matrix, model):
        objective_expr = gp.quicksum(target_matrix[i][j] * x[i, j] for i in range(n) for j in range(m))
        model.setObjective(objective_expr, GRB.MINIMIZE)
        return model
