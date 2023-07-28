import getdata
from getinterval import GetInterval
import taxiingtime_matrix
import variable
import outputdata
from optimization import Optimization


def generante_solution(filename, regulation, seuil, t_or_a, part, delta):
    optim_temp = Optimization()
    sheetname = optim_temp.find_numbers(filename)
    airline = getdata.load_airlinsgate()
    data = getdata.load_traffic(filename)
    taxiingtime = getdata.load_taxitime(regulation)
    wingsize = getdata.load_wingsize()
    generante_interval = GetInterval()
    second_interval = generante_interval.presolve(t_or_a, data, seuil, delta)
    # outputdata.write_interval(second_interval, sheetname)
    second_interval_data = second_interval[0]
    interval_flight = second_interval[2]
    # print(interval_data['end_interval'])
    interval_pattern = second_interval[1]
    quarter = 0
    result_set = variable.variable(second_interval_data, airline, wingsize, part, interval_flight, data, quarter)
    interval_data = result_set[0]
    interval_set = result_set[1]
    gate_set = result_set[2]
    taxi_matrix = taxiingtime_matrix.taxiingtime_matrix(taxiingtime, interval_data, interval_pattern)
    obstruction = variable.get_obstruction(interval_data, interval_set)
    target_matrix = variable.target_gen(taxi_matrix, wingsize, interval_set, gate_set)
    x = result_set[3]
    gate_set = result_set[2]
    result = optim_temp.optim(x, obstruction, target_matrix, part)
    gate_choose = result[1]

    # 构建gate_choose
    temp_1 = []
    temp_2 = []
    temp_3 = []
    for i in range(len(gate_choose)):
        index = interval_set[i]
        temp_1.append(interval_data['begin_callsign'][index])
        temp_2.append(interval_data['registration'][index])
        temp_3.append(gate_choose[i])
    my_key = ['begin_callsign', 'registration', 'gate']
    default_value = []
    gate_dict = dict.fromkeys(my_key, default_value)
    gate_dict['begin_callsign'] = temp_1
    gate_dict['registration'] = temp_2
    gate_dict['gate'] = temp_3

    outputdata.write_xls(gate_dict, sheetname, gate_set)
    return gate_dict
