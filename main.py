# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import plot
import os
import GenernateSolution
import reallocation


part = 3
delta = 5
seuil = 28
regulation = 3
quarter = 0

if __name__ == '__main__':
    # 指定文件夹路径
    folder_path = './data/error-in-data'
    # folder_path = './data/error-in-data/buffer'

    # 遍历文件夹中的文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):  # 判断文件是否以 .csv 结尾
            filename = os.path.join(folder_path, filename)

            # allocation reallocation local search
            results = GenernateSolution.generante_solution(filename, regulation, seuil, quarter, part, delta)
            genernate_solution = results[0]
            pattern = results[1]
            re_solution = reallocation.reallocation(filename, seuil, part, delta, genernate_solution, regulation,
                                                    pattern)

            # 增加航班

