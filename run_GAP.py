import os
import tracemalloc
from BasicFunction.GetData import get_data
from GateAllocation.GateAllocation import GateAllocation
from GateAllocation.OutPut import OutPut
from GateAllocation.reAllocation import ReAllocation

if __name__ == "__main__":

    folder_path = "./data/error-in-data"
    out_path = "./results/re_Traffic_GAP_mix\\"
    seuil = 28
    pattern_list = ["MANEX", "PN_MANEX"]

    for pattern in pattern_list:
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                tracemalloc.start()

                quarter = 0
                result_list = []

                filename = os.path.join(folder_path, filename)

                data = get_data(filename)
                init_result = GateAllocation(data, seuil, pattern).optimization(sans_taxiing_time=False)
                last_result = init_result

                while True:
                    last_result = ReAllocation(data, seuil, pattern, quarter, init_result,
                                               last_result).optimization(sans_taxiing_time=False)
                    result_list.append(last_result)

                    quarter += 1
                    if quarter == 100:
                        break

                    current, peak = tracemalloc.get_traced_memory()
                    print(f"当前时刻为：{quarter}")
                    print(f"当前内存使用：{current / 10 ** 6}MB")
                    print(f"峰值内存使用：{peak / 10 ** 6}MB")

                OutPut(data, filename, out_path, pattern).output_process(result_list)
                OutPut(data, filename, out_path, pattern).output_final(last_result)

                tracemalloc.stop()

                print("\033[32m" + filename + "\033[0m")
