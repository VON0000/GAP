import os
import re

import pandas as pd

folder_path = '../results/Traffic_GAP_2Pistes/'

if __name__ == "__main__":
    for filename in os.listdir(folder_path):
        match = re.search(r"process", filename, re.M | re.I)
        if match is None and filename.endswith(".csv"):
            filename = os.path.join(folder_path, filename)
            df = pd.read_csv(filename)

            # 将numbers列的元素转换为字符串，并检查是否包含".0"
            gate_error = df['Parking'].astype(str).str.contains('\.0')

            for g in gate_error:
                if g:
                    print(filename)
                    break
