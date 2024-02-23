import os

import pandas as pd

folder_path = '../Traffic_GAP_2Pistes/'


# 定义一个转换函数，尝试转换为整数，失败则保留原值
def try_convert(x):
    try:
        # 尝试将x转换为浮点数再转为整数
        return int(float(x))
    except ValueError:
        # 转换失败时返回原始x
        return x


if __name__ == "__main__":
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            filename = os.path.join(folder_path, filename)

            df = pd.read_csv(filename)
            parking_columns = df.filter(like='Parking').columns
            for column in parking_columns:
                df[column] = df[column].apply(try_convert)
            df.to_csv(filename, index=False)
