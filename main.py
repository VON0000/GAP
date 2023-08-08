# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import plot
import os
import GenernateSolution
import reallocation


part = 3
t_or_a = 0
delta = 5
seuil = 28
regulation = 1
quarter = 0
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # 指定文件夹路径
    folder_path = './data/error-in-data'

    # 遍历文件夹中的文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):  # 判断文件是否以 .csv 结尾
            filename = os.path.join(folder_path, filename)
            # filename = "./data/error-in-data/gaptraffic-2017-08-03-new.csv"
            results = GenernateSolution.generante_solution(filename, regulation, seuil, t_or_a, part, delta)
            genernate_solution = results[0]
            pattern = results[1]
            re_solution = reallocation.reallocation(filename, seuil, part, delta, genernate_solution, regulation, pattern)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
