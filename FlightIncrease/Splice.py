import os
import pandas as pd
import re


def find_number_in_filename(filename):
    # 使用正则表达式找到文件名中的数字
    numbers = re.findall(r"\d+", filename)
    numbers = "".join(numbers)
    return numbers if numbers else None


def concatenate_files_with_same_number(folder1, folder2, output_folder):
    # 创建输出文件夹如果它不存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取两个文件夹中的所有CSV文件
    files_in_folder1 = {
        f: find_number_in_filename(f)
        for f in os.listdir(folder1)
        if f.endswith(".csv") and "process" not in f
    }
    files_in_folder2 = {
        f: find_number_in_filename(f)
        for f in os.listdir(folder2)
        if f.endswith(".csv") and "process" not in f
    }

    # 匹配具有相同数字的文件
    for file1, number1 in files_in_folder1.items():
        for file2, number2 in files_in_folder2.items():
            if number1 == number2:
                # 读取CSV文件
                df1 = pd.read_csv(os.path.join(folder1, file1))
                df2 = pd.read_csv(os.path.join(folder2, file2))

                # 按行拼接数据
                concatenated_df = pd.concat([df1, df2], axis=0)

                # 输出到新的CSV文件
                output_filename = f"concatenated_{number1}.csv"
                concatenated_df.to_csv(
                    os.path.join(output_folder, output_filename), index=False
                )


# 使用函数
folder_path1 = "../results/gate_5_taxi_15/"
folder_path2 = "../results/IncreaseFlight_type/"
output_path = "../results/ConcatenatedFiles_type/"

concatenate_files_with_same_number(folder_path1, folder_path2, output_path)
