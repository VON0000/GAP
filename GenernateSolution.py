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
    interval = generante_interval.presolve(t_or_a, data, seuil, delta)
    interval_data = interval[0]
    # print(interval_data['end_interval'])
    interval_pattern = interval[1]
    taxi_matrix = taxiingtime_matrix.taxiingtime_matrix(taxiingtime, interval_data, interval_pattern)
    result_set = variable.variable(interval_data, airline, wingsize, part)
    obstruction = variable.get_obstruction(interval_data, airline, wingsize, part)
    target_matrix = variable.target(taxi_matrix, interval_data, airline, wingsize, part)
    x = result_set[3]
    gate_set = result_set[2]
    result = optim_temp.optim(x, obstruction, target_matrix, part)
    outputdata.write_xls(result, sheetname, gate_set)
    gate_choose = result[1]
    return gate_choose
