"""
按照 second 已经转化为 half-minute 来考虑
"""
from BasicFunction.GetData import get_right_time


def _count_numbers_in_range(lst, low, high):
    count = 0
    for num in lst:
        if high == 24 * 60 * 60:
            if low <= num:
                count += 1
            continue
        if low <= num < high:
            count += 1
    return count


class AircraftTide:
    """
    为 interval 设置 QFU 属性
    """

    def __init__(self, data: dict, quarter: int, seuil: int):
        self.data = data
        self.quarter = quarter
        self.seuil = seuil
        self.time_tide = self.get_time_tide()

    def get_time_tide(self):
        """
        获取航班潮汐
        大于 seuil -> True
        小于 seuil -> False
        """
        time_tide = {}

        time_list = self._get_time_used()

        for i in range(24):
            counter = _count_numbers_in_range(time_list, i * 60 * 60, (i + 1) * 60 * 60)
            if counter > self.seuil:
                time_tide[i] = True
            else:
                time_tide[i] = False

        return time_tide

    def _get_time_used(self) -> list:
        """
        查找需要使用的时间
        """

        time_list = []

        for i in range(len(self.data["data"])):
            time_list.append(get_right_time(self.data, i, self.data["callsign"][i].split(maxsplit=1)[1], self.quarter))

        return time_list
