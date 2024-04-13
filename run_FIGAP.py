import os
import tracemalloc

from BasicFunction.AvailableGateStrategy import get_available_gate_FIGAP
from BasicFunction.GetData import get_data
from GateAllocation.GateAllocation import GateAllocation
from GateAllocation.OutPutGAP import OutPutGAP
from GateAllocation.reAllocation import ReAllocation

if __name__ == "__main__":

    folder_path = "./results/intermediateFile/re_concatenated_0.4"
    out_path = "./results/re_Traffic_Augmente_GAP_2Pistes_0.4\\"
    seuil = 0
    pattern_list = ["MANEX"]

    for pattern in pattern_list:
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                tracemalloc.start()

                quarter = 0
                result_list = []

                filename = os.path.join(folder_path, filename)

                data = get_data(filename)
                init_result = GateAllocation(data, seuil, pattern,
                                             available_gate_strategy=get_available_gate_FIGAP).optimization(
                    sans_taxiing_time=False)
                last_result = init_result

                print("初次分配已完成，开始迭代分配")

                while True:
                    last_result = ReAllocation(data, seuil, pattern, quarter, init_result, last_result,
                                               available_gate_strategy=get_available_gate_FIGAP).optimization(
                        sans_taxiing_time=False)

                    if last_result == {}:
                        break

                    result_list.append(last_result)

                    quarter += 1
                    if quarter == 100:
                        break

                    current, peak = tracemalloc.get_traced_memory()
                    print(f"当前时刻为：{quarter}")
                    print(f"当前内存使用：{current / 10 ** 6}MB")
                    print(f"峰值内存使用：{peak / 10 ** 6}MB")

                OutPutGAP(data, filename, out_path, pattern).output_process(result_list)
                OutPutGAP(data, filename, out_path, pattern).output_final(last_result)

                tracemalloc.stop()

                print("\033[32m" + filename + "\033[0m")
