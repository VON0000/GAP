import xlwt


def write_xls(result, sheetname, gate_set):
    sheetname = ' '.join(sheetname)
    optim_time = result[0]
    gate_choose = result[1]
    obj = result[2]

    wb = xlwt.Workbook()
    # 添加一个表
    ws = wb.add_sheet(sheetname)

    # 3个参数分别为行号，列号，和内容
    # 需要注意的是行号和列号都是从0开始的
    ws.write(0, 0, 'optim_time')
    ws.write(0, 1, 'obj')
    ws.write(0, 2, 'interval')
    ws.write(0, 3, 'gate_choose')

    ws.write(1, 0, optim_time)
    ws.write(1, 1, obj)

    for i in range(len(gate_choose)):
        index = int(gate_choose[i])
        ws.write(i + 1, 2, i+1)
        ws.write(i+1, 3, gate_set[index])

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
