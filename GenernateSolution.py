import getdata
from getinterval import GetInterval
from taxiingtime_matrix import Matrix
import variable
from outputdata import ToCsv
from optimization import Optimization


def generante_solution(filename, regulation, seuil, quarter, part, delta):
    """

    :param filename: the file which is calculated now
    :param regulation: PN or NP
    :param seuil: to determine to use 16R or 16L
    :param quarter: every 15 minutes
    :param part: the airline group
    :param delta: buffer
    :return: the gate for each flight

    Calculate the allocation of parking stands for flights belonging to specific airlines,
    under a specific taxiing mode. This time, the solution is for a one-time parking stand
    allocation within a day, where flights departing and arriving between 0:00 and 0:15
    use actual time, while others use target time.
    """
    # Initialize
    optim_temp = Optimization()
    sheetname = optim_temp.find_numbers(filename)
    generante_interval = GetInterval()
    matrix = Matrix()
    to_csv = ToCsv()

    # Import data
    airline = getdata.load_airlinsgate()
    data = getdata.load_traffic(filename)
    taxiingtime = getdata.load_taxitime(regulation)
    wingsize = getdata.load_wingsize()

    # Calculate interval in half-minute
    second_interval = generante_interval.presolve(quarter, data, seuil, delta)
    second_interval_data, interval_pattern, interval_flight, pattern = second_interval

    # Get optimization variables
    result_set = variable.variable(second_interval_data, airline, wingsize, part, interval_flight, data, quarter)
    interval_data, interval_set, gate_set, x = result_set

    # Get intervals with mutual conflicts
    obstruction = variable.get_obstruction(interval_data, interval_set)

    # Calculate the objective function
    target_matrix = matrix.target_gen(wingsize, interval_set, gate_set, part, interval_data, airline, taxiingtime,
                                      interval_pattern)

    # Optimization
    result = optim_temp.optim(x, obstruction, target_matrix, part)
    gate_choose = result[1]

    # Result
    gate_dict = variable.SpecialVariable.get_aim_dict(gate_choose, interval_set, interval_data)
    # outputdata.write_other(gate_dict, sheetname, gate_set, pattern, regulation)
    # to_csv.write_process(gate_dict, sheetname, gate_set, regulation, quarter)
    return gate_dict, pattern
