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
    second_interval_data = second_interval[0]
    # print(interval_data['end_interval'])
    interval_pattern = second_interval[1]
    result_set = variable.variable(second_interval_data, airline, wingsize, part)
    interval_data = result_set[0]
    interval_set = result_set[1]
    gate_set = result_set[2]
    taxi_matrix = taxiingtime_matrix.taxiingtime_matrix(taxiingtime, interval_data, interval_pattern)
    obstruction = variable.get_obstruction(interval_data, interval_set)
    target_matrix = variable.target(taxi_matrix, wingsize, interval_set, gate_set)
    x = result_set[3]
    gate_set = result_set[2]
    result = optim_temp.optim(x, obstruction, target_matrix, part)
    outputdata.write_xls(result, sheetname, gate_set)
    gate_choose = result[1]
    return gate_choose
