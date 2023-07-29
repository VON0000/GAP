import xlwt


def write_xls(gate_dict, sheetname, gate_set, interval_data, interval_set):
    sheetname = ' '.join(sheetname)

    wb = xlwt.Workbook()
    # 添加一个表
    ws = wb.add_sheet(sheetname)

    # 3个参数分别为行号，列号，和内容
    # 需要注意的是行号和列号都是从0开始的
    ws.write(0, 0, 'call_sign_1')
    ws.write(0, 1, 'call_sign_2')
    ws.write(0, 2, 'registration')
    ws.write(0, 3, 'gate')
    ws.write(0, 4, 'begin time')
    ws.write(0, 5, 'finish time')

    for i in range(len(gate_dict['gate'])):
        ws.write(i + 1, 0, gate_dict['begin_callsign'][i])
        try:
            ws.write(i + 1, 1, gate_dict['end_callsign'][i])
        except KeyError:
            pass
        ws.write(i + 1, 2, gate_dict['registration'][i])
        ws.write(i + 1, 3, gate_set[gate_dict['gate'][i]])
        ws.write(i + 1, 4, interval_data['begin_interval'][interval_set[i]])
        ws.write(i + 1, 5, interval_data['end_interval'][interval_set[i]])

    # 保存excel文件
    wb.save('E:/gap/results/python/buffer/result.xls')


def write_interval(result, sheetname):
    sheetname = ' '.join(sheetname)
    interval_data = result[0]

    wb = xlwt.Workbook()
    # 添加一个表
    ws = wb.add_sheet(sheetname)

    # 3个参数分别为行号，列号，和内容
    # 需要注意的是行号和列号都是从0开始的
    my_key = ['interval', 'begin_interval', 'end_interval', 'airline', 'registration', 'begin_callsign',
              'end_callsign', 'wingspan']
    for i in range(len(my_key)):
        ws.write(0, i, my_key[i])

    for i in range(len(my_key)):
        for j in range(len(interval_data['interval'])):
            ws.write(j + 1, i, interval_data[my_key[i]][j])

    # 保存excel文件
    wb.save('E:/gap/results/python/buffer/interval.xls')
