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
    filename = "E:/gap/error-in-data/gaptraffic-2017-08-03-new.csv"
    genernate_solution = GenernateSolution.generante_solution(filename, regulation, seuil, t_or_a, part, delta)
    reallocation.reallocation(filename, seuil, part, delta, genernate_solution)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
