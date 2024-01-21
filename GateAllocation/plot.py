import json
import sys
from random import choice

import numpy as np

sys.path.append('E:/pycharm/gantt-master/gantt-master')
from gantt import Gantt


def make_json(gen_x, interval_data):
    colors = ["cyan", "deepskyblue", "dodgerblue", "yellow", "chartreuse", "lime", "blue", "violet", "orange", "red"]
    gate_set = []
    total_data = []
    for i in range(len(gen_x['gate'])):
        temp_1 = np.where(np.array(interval_data['begin_callsign']) == gen_x['begin_callsign'][i])[0]
        if len(temp_1) == 1:
            data = {"label": str(gen_x['gate'][i]), "start": interval_data['begin_interval'][temp_1[0]],
                    "end": interval_data['end_interval'][temp_1[0]], "color": choice(colors)}
        else:
            temp_2 = np.where(np.array(interval_data['registration']) == gen_x['registration'][i])[0]
            temp = list(set(temp_1) & set(temp_2))
            data = {"label": str(gen_x['gate'][i]), "start": interval_data['begin_interval'][temp[0]],
                    "end": interval_data['end_interval'][temp[0]], "color": choice(colors)}
        total_data.append(data)

    xticks = []
    x = 0
    while x <= 3000:
        xticks.append(x)
        x = x + 100
    dic = {"packages": total_data, "title": "Gantt", "xlabel": "time", "xticks": xticks}
    return dic


def dict2json(file_name, the_dict, quarter):
    """

    将字典文件写如到json文件中
    :param file_name: 要写入的json文件名(需要有.json后缀),str类型
    :param the_dict: 要写入的数据，dict类型
    :return: 1代表写入成功,0代表写入失败
    """
    try:
        assert quarter >= 84
        json_str = json.dumps(the_dict, indent=2)
        with open(file_name, 'w', encoding="gbk") as json_file:
            json_file.write(json_str)

        # file = open(file_name, "r", encoding="utf-8")
        # file2 = open('E:/gap/results/python/buffer/j_data2.json', "w", encoding="gbk")
        #
        # for i in file:
        #     file2.writelines(i)
        #
        # file2.close()
        # file.close()

        p = Gantt(file_name)
        p.render()
        p.show()
        p.savefit(''.join(['E:/pycharm/GAP/results/20230924/', quarter, '.png']))
        return 1
    except:
        return 0
