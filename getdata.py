# 读取数据
import pandas as pd


def load_wingsize():
    data = pd.read_excel("E:/gap/data2/wingsizelimit.xls", sheet_name=None)
    sheet_data = data['sheet1']
    wingsize = {}
    for i in sheet_data.index:
        # print(sheet_data['gate'][i], end=' ')
        # print(sheet_data['size_limit'][i])
        wingsize[str(sheet_data['gate'][i])] = sheet_data['size_limit'][i]
    # print(wingsize)
    return wingsize


def load_airlinsgate():
    airlines_data = pd.read_csv("E:/gap/data2/airlinesgate.csv", header=0, usecols=["airlines"])
    airlines = {}
    with open("E:/gap/data2/airlinesgate.csv", 'r') as gate:
        lines = gate.readlines()
        counter = 0
        gate_data = []
        for i in lines:
            counter += 1
            temp = i.split(',')
            gate_set = []
            for j in temp:
                j = j.strip()
                if j != "":
                    gate_set.append(j)
            gate_set.pop(0)
            gate_data.append(gate_set)
    wingsize = load_wingsize()
    gate_list = list(wingsize.keys())
    temp = gate_list[73:116]
    temp.extend(gate_list[128:139])
    for i in range(0, counter-1):
        if gate_data[i+1] not in ['cargo', 'general', 'corporate']:
            airlines[airlines_data['airlines'][i]] = gate_data[i+1]
        else:
            airlines[airlines_data['airlines'][i]] = temp
    # print(airlines)
    return airlines


def load_traffic(filename):
    data = pd.read_csv(filename)
    data = data.to_dict(orient='list')
    # print(data)
    n = len(data['data'])
    for i in range(n):
        if data['arrivee'][i] == 'ZBTJ':
            data['callsign'][i] = data['callsign'][i] + ' ar'
        else:
            data['callsign'][i] = data['callsign'][i] + ' de'
    return data


def load_taxitime(regulation):
    data = pd.read_excel("E:/gap/data2/mintaxitime.xlsx", sheet_name=None, header=2)
    sheet_data = data['sheet1']
    # print(sheet_data['DEP-16R'])
    taxitime = {}
    for i in sheet_data.index:
        if regulation == 1:
            taxitime[sheet_data['Gate'][i]] = [sheet_data['DEP-16R'][i],
                                               sheet_data['ARR-16L'][i], sheet_data['ARR-16R'][i]]
        elif regulation == 2:
            taxitime[sheet_data['Gate'][i]] = [sheet_data['DEP-16R.1'][i],
                                               sheet_data['ARR-16L.1'][i], sheet_data['ARR-16R.1'][i]]
        elif regulation == 3:
            taxitime[sheet_data['Gate'][i]] = [sheet_data['DEP-16R.2'][i],
                                               sheet_data['ARR-16L.2'][i], sheet_data['ARR-16R.2'][i]]
        else:
            taxitime[sheet_data['Gate'][i]] = [sheet_data['DEP-16R.3'][i],
                                               sheet_data['ARR-16L.3'][i], sheet_data['ARR-16R.3'][i]]
    wingsize = load_wingsize()
    gate_list = list(wingsize.keys())
    taxiingtime = {}
    for gate in gate_list:
        taxiingtime[str(gate)] = taxitime[str(gate)]
    return taxiingtime
