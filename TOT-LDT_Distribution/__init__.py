import math
import sys
import os
sys.path.append("..")
from GateAllocation import getdata
from GateAllocation.getinterval import GetInterval
from GateAllocation.optimization import Optimization
import numpy as np
import matplotlib.pyplot as plt
import re
from itertools import chain


class GetNewInterval(GetInterval):
    @staticmethod
    def longtime_arrivee(i, ldt):
        m = 60
        begin_interval = ldt[i] + 10 * m
        end_interval = ldt[i] + 60 * 24 * m
        interval = end_interval - begin_interval
        return interval, begin_interval, end_interval

    @staticmethod
    def longtime_departure(i, tot):
        m = 60
        begin_interval = tot[i] - 60 * 24 * m
        end_interval = tot[i] - 10 * m
        interval = end_interval - begin_interval
        return interval, begin_interval, end_interval

    @staticmethod
    def actual_target(data, t_or_a):
        if t_or_a == 0:
            tot = data['TTOT']
            ldt = data['TLDT']
        else:
            tot = data['ATOT']
            ldt = data['ALDT']
        return tot, ldt

    def get_interval(self, data, departure_set, num, pattern, tot, ldt):
        """

        Get the parking interval for each aircraft
        """
        zbtj_time = []
        for i in num:
            if i in departure_set:
                zbtj_time.append(tot[i])
            else:
                zbtj_time.append(ldt[i])
        sorted_indices = [i for i, _ in sorted(enumerate(zbtj_time), key=lambda x: x[1])]
        # print(zbtj_time)
        sorted_indices = sorted_indices + num[0]
        # print(sorted_indices)
        h = 60 * 60
        i = 0
        my_key = ['interval', 'begin_interval', 'end_interval', 'airline', 'registration', 'begin_callsign',
                  'end_callsign', 'wingspan']
        my_values = [[], [], [], [], [], [], [], []]
        interval_data = {k: v for k, v in zip(my_key, my_values)}
        interval_pattern = []
        interval_flight = []
        while i < len(sorted_indices):
            if sorted_indices[i] in departure_set:
                interval_data = self.interval_value(data, i, self.longtime_departure, sorted_indices,
                                                    interval_data, tot)
                interval_pattern.append([0, pattern[sorted_indices[i]]])
                interval_flight.append([sorted_indices[i]])
                # print(interval_data)
                i = i + 1
            else:
                if i + 1 < len(sorted_indices):
                    temp = self.shorttime(i, ldt, tot, sorted_indices)
                    interval_data['interval'].append(temp[0])
                    interval_data['begin_interval'].append(temp[1])
                    interval_data['end_interval'].append(temp[2])
                    interval_data['airline'].append(data['Airline'][sorted_indices[i]])
                    interval_data['registration'].append(data['registration'][sorted_indices[i]])
                    interval_data['begin_callsign'].append(data['callsign'][sorted_indices[i]])
                    interval_data['end_callsign'].append(data['callsign'][sorted_indices[i + 1]])
                    interval_data['wingspan'].append(data['Wingspan'][sorted_indices[i]])
                    # print(interval_data)
                    interval_pattern.append([pattern[sorted_indices[i]], pattern[sorted_indices[i + 1]]])
                    interval_flight.append([sorted_indices[i], sorted_indices[i + 1]])
                else:
                    interval_data = self.interval_value(data, i, self.longtime_arrivee, sorted_indices,
                                                        interval_data, ldt)
                    interval_pattern.append([pattern[sorted_indices[i]], 0])
                    interval_flight.append([sorted_indices[i]])
                    # print(interval_data)
                i = i + 2
        # print(interval_data)
        return interval_data, interval_pattern, interval_flight


def get_number_of_interval(filename: str, seuil: int, quarter: int, delta: int):
    # Initialize
    generante_interval = GetNewInterval()

    # Import data
    data = getdata.load_traffic(filename)

    # Calculate interval in half-minute
    second_interval = generante_interval.presolve(quarter, data, seuil, delta)
    second_interval_data, interval_pattern, interval_flight, pattern = second_interval

    n = len(second_interval_data['airline'])
    hour_list = [(0, 29), (30, 39), (40, 49), (50, 59), (60, math.inf)]
    # h = 60 * 30
    # for i in range(48):
    #     hour_list.append((i * h, (i + 1) * h + 1))
    counter_list = [0] * len(hour_list)
    for i in second_interval_data['interval']:
        for h, (start, end) in enumerate(hour_list):
            if start <= int(i) / 60 <= end:
                counter_list[h] += 1
    return counter_list


def bar_pci(counter_list, filename):
    x = [30, 40, 50, 60, math.inf]
    xticks = np.arange(len(x))

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.bar(xticks, counter_list, width=0.25, label='number', color='sandybrown')
    plt.rcParams.update({'font.size': 15})
    plt.legend(loc='upper right')

    ax.legend()
    plt.tick_params(labelsize=17)

    # 最后调整x轴标签的位置
    xticks_new = list(chain.from_iterable(zip(xticks - 0.125, xticks + 0.125)))
    xticklabels_new = list(chain.from_iterable(zip(['0', ' 30', '40', '50', '60'], ['29', '39', '49', '59', 'Inf'])))
    ax.set_xticks(xticks_new)
    ax.set_xticklabels(xticklabels_new)
    ax.set_xlabel("Time (min)", fontsize=17)
    ax.set_ylabel("the Number of Interval", fontsize=17)

    # 设置画布颜色和边框
    ax.set_facecolor("white")
    ax.spines['top'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')

    for i in range(len(counter_list)):
        xy = (xticks[i] - 0.03, counter_list[i] * 1.003)
        s = str(counter_list[i])
        ax.annotate(
            text=s,  # 要添加的文本
            xy=xy,  # 将文本添加到哪个位置
            fontsize=15,  # 标签大小
            color="black",  # 标签颜色
            ha="center",  # 水平对齐
            va="baseline"  # 垂直对齐
        )
    filename = re.findall(r'\d+', filename)
    ax.set_title(str(filename), fontsize=17)

    plt.savefig(str(filename) + '.png')
    plt.show()


if __name__ == '__main__':
    delta = 5
    seuil = 28

    # Specify the folder path
    avant_folder_path = os.path.abspath(os.path.join(os.path.dirname('settings.py'), os.path.pardir))

    folder_path = avant_folder_path + '\\data\\error-in-data'
    # folder_path = './data/error-in-data/buffer'

    # Iterate through the files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):  # Check if the file ends with .csv
            filename = os.path.join(folder_path, filename)

            # Generate initial solution
            counter_list = get_number_of_interval(filename, seuil, 1, delta)
            bar_pci(counter_list, filename)
