import getdata
from getinterval import GetInterval
from taxiingtime_matrix import Matrix
import variable
from outputdata import ToCsv
from optimization import Optimization


def generante_solution(filename, regulation, seuil, quarter, part, delta):
    # 初始化及导入数据
    optim_temp = Optimization()
    sheetname = optim_temp.find_numbers(filename)
    airline = getdata.load_airlinsgate()
    data = getdata.load_traffic(filename)
    taxiingtime = getdata.load_taxitime(regulation)
    wingsize = getdata.load_wingsize()
    generante_interval = GetInterval()
    matrix = Matrix()
    to_csv = ToCsv()

    # 计算interval 按照每半分钟
    second_interval = generante_interval.presolve(quarter, data, seuil, delta)
    second_interval_data = second_interval[0]
    interval_flight = second_interval[2]
    # print(interval_data['end_interval'])
    interval_pattern = second_interval[1]
    pattern = second_interval[3]
    result_set = variable.variable(second_interval_data, airline, wingsize, part, interval_flight, data, quarter)
    interval_data = result_set[0]
    interval_set = result_set[1]
    gate_set = result_set[2]

    # 计算目标函数 时间冲突
    obstruction = variable.get_obstruction(interval_data, interval_set)
    target_matrix = matrix.target_gen(wingsize, interval_set, gate_set, part, interval_data, airline, taxiingtime,
                                      interval_pattern)

    # 获得x
    x = result_set[3]

    # 优化
    result = optim_temp.optim(x, obstruction, target_matrix, part)
    gate_choose = result[1]

    # 构建gate_choose
    temp_1 = []
    temp_2 = []
    temp_3 = []
    temp_4 = []
    for i in range(len(gate_choose)):
        index = interval_set[i]
        temp_1.append(interval_data['begin_callsign'][index])
        temp_2.append(interval_data['registration'][index])
        temp_3.append(gate_choose[i])
        temp_4.append(interval_data['end_callsign'][index])
    my_key = ['begin_callsign', 'registration', 'gate', 'end_callsign']
    default_value = []
    gate_dict = dict.fromkeys(my_key, default_value)
    gate_dict['begin_callsign'] = temp_1
    gate_dict['registration'] = temp_2
    gate_dict['gate'] = temp_3
    gate_dict['end_callsign'] = temp_4
    # outputdata.write_other(gate_dict, sheetname, gate_set, pattern, regulation)
    # to_csv.write_process(gate_dict, sheetname, gate_set, regulation, quarter)
    return gate_dict, pattern
