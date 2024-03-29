import os

from BasicFunction.GetData import get_data
from refactorGateAllocation.GateAllocation import GateAllocation
from refactorGateAllocation.OutPut import OutPut
from refactorGateAllocation.reAllocation import ReAllocation

if __name__ == "__main__":

    folder_path = "../results/Traffic_GAP_2Pistes"
    out_path = "../results/Traffic_GAP_2Pistes_ReAllocation"
    seuil = 28
    pattern = "MANEX"
    quarter = 0

    result_list = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            filename = os.path.join(folder_path, filename)

            data = get_data(filename)
            init_result = GateAllocation(data, seuil, pattern).optimization()
            last_result = init_result

            while True:
                last_result = ReAllocation(data, seuil, pattern, quarter, init_result, last_result).optimization()
                result_list.append(last_result)

                quarter += 1
                if quarter == 100:
                    break

            OutPut(data, filename, out_path).output_process(result_list)
            OutPut(data, filename, out_path).output_final(last_result)
