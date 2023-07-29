import json
import sys
from random import choice
sys.path.append('E:/pycharm/gantt-master/gantt-master')
from gantt import Gantt


def make_json(gen_x, interval_set, interval_data):
    gate_set = []
    for i in range(len(gen_x)):
        for j in range(len(gen_x[i])):
            if gen_x[i][j] == 1:
                gate_set.append(j)
    total_data = []
    colors = ["cyan", "deepskyblue", "dodgerblue", "yellow", "chartreuse", "lime", "blue", "violet", "orange", "red"]
    for i in range(len(interval_set)):
        data = {"label": str(gate_set[i]), "start": interval_data['begin_interval'][interval_set[i]],
                "end": interval_data['end_interval'][interval_set[i]], "color": choice(colors)}
        total_data.append(data)
    xticks = []
    x = 0
    while x <= 3000:
        xticks.append(x)
        x = x + 100
    dic = {"packages": total_data, "title": "Gantt", "xlabel": "time", "xticks": xticks}
    return dic


def dict2json(file_name, the_dict):
    '''
    将字典文件写如到json文件中
    :param file_name: 要写入的json文件名(需要有.json后缀),str类型
    :param the_dict: 要写入的数据，dict类型
    :return: 1代表写入成功,0代表写入失败
    '''
    try:
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
        return 1
    except:
        return 0