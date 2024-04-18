import copy
import random
import re
from typing import Union, Tuple

import loguru

from BasicFunction.AirlineType import AirlineType
from FlightIncrease.DelayTime import delay_time
from BasicFunction.GetGateAttribute import GetGateAttribute
from BasicFunction.IntervalType import IntervalBase


def is_overlapping(time1, time2) -> bool:
    """
    判断两个时间段是否有重叠
    False 为没有冲突
    True 为有冲突
    """
    if time1[0] <= time2[0] <= time1[1]:
        return True
    if time2[0] <= time1[0] <= time2[1]:
        return True
    return False


def _conflict_half(
        aug_inst: IntervalBase, inst: IntervalBase, gate: str, flag: bool
) -> bool:
    """
    False 为没有冲突
    True 为有冲突
    """
    if (inst.gate == gate) or ([inst.gate] == re.findall(r"\d+", gate)):
        flag = is_overlapping(
            (inst.begin_interval, inst.end_interval),
            (aug_inst.begin_interval, aug_inst.end_interval),
        )
    return flag


def _conflict_all(
        aug_inst: IntervalBase, inst: IntervalBase, gate: str, flag: bool
) -> bool:
    """
    False 为没有冲突
    True 为有冲突
    """
    if re.findall(r"\d+", inst.gate) == re.findall(r"\d+", gate):
        flag = is_overlapping(
            (inst.begin_interval, inst.end_interval),
            (aug_inst.begin_interval, aug_inst.end_interval),
        )
    return flag


def find_conflict(aug_inst: IntervalBase, gate: str, interval: list) -> bool:
    """
    检查当前停机坪是否有与添加interval冲突的interval
    False 为没有冲突
    True 为有冲突
    """
    flag = False
    counter = 0
    while not flag and counter < len(interval):
        inst = interval[counter]
        # 414
        if not (("L" in gate) or ("R" in gate)):
            flag = _conflict_all(aug_inst, inst, gate, flag)
        # 414L 414R
        else:
            flag = _conflict_half(aug_inst, inst, gate, flag)
        counter = counter + 1
    return flag


def find_suitable_gate(inst: IntervalBase, interval: list) -> Union[IntervalBase, None]:
    """
    找到一个能停靠的停机坪
    """
    available_gate = []
    gate = AirlineType(inst.airline).airline_gate
    for g in gate:
        if inst.wingspan <= GetGateAttribute(g).size:
            if not find_conflict(inst, g, interval):
                available_gate.append(g)
    if len(available_gate) == 0:
        return None
    else:
        inst.gate = random.choice(available_gate)
        return inst


def get_map_al(inst: IntervalBase, interval_list: list) -> list:
    """
    为对应的航班根据尾流间隔推迟时间，查找是否有合适的机位
    """
    ref_inst = get_ref_inst(inst, interval_list)
    ref_inst = copy.deepcopy(ref_inst)

    assert ref_inst != [], "No reference interval found" + str(inst.begin_callsign) + str(inst.registration)

    ref_inst = delay_time(ref_inst, interval_list, "TLDT")
    if not ref_inst:
        return []
    ref_inst = find_suitable_gate_total(ref_inst, interval_list)
    return ref_inst


def get_ref_inst(inst: IntervalBase, interval_list: list) -> list:
    """
    获取inst的在actual time下的对应航班
    """
    if inst.begin_callsign == inst.end_callsign:
        inst_type = inst.begin_callsign[-2:].rstrip()
        if inst_type == "ar":
            ref_inst = [il for il in interval_list if
                        il.begin_callsign == inst.begin_callsign and il.registration == inst.registration]
            return ref_inst

        ref_inst = [il for il in interval_list if
                    il.end_callsign == inst.end_callsign and il.registration == inst.registration]
        return ref_inst

    ref_inst = [il for il in interval_list if (
            il.begin_callsign == inst.begin_callsign or il.end_callsign == inst.end_callsign) and
                il.registration == inst.registration]
    return ref_inst


def find_suitable_gate_total(add_list: list, interval_list: list) -> list:
    for al in add_list:
        al = find_suitable_gate(al, interval_list)
        if al is None:
            return []
    return add_list


def judge_in_actual(add_list: list, actual_list: list) -> Tuple[list, list]:
    """
    校验通过target time增加的航班 在actual time下是否也能找到停机位
    """
    ref_list = []
    for al in add_list:
        ref_inst = get_map_al(al, actual_list)
        ref_list.extend(ref_inst)
        if not ref_inst:
            return [], []
    return add_list, ref_list


def judge_inst_in_one_hour(inst: IntervalBase) -> bool:
    """
    判断航班的target time是否在一天的一个小时内
    false 为不在
    true 为在
    不增加 target 时间在一个小时内的航班
    """
    if inst.begin_callsign == inst.end_callsign:
        inst.type = inst.begin_callsign[-2:].rstrip()
        if inst.type == "de":
            return inst.time_dict["de"]["TTOT"] <= 60 * 60
        return inst.time_dict["ar"]["TLDT"] <= 60 * 60

    # 如果是ar + de，只要ar在一个小时内，就不增加(de 在一个小时内，ar 必在一个小时内)
    if inst.time_dict["ar"]["TLDT"] <= 60 * 60:
        return True


class IncreaseFlight:
    def __init__(self, actual_list: list, rate: float = 1):
        self.rate = rate
        self.interval = copy.deepcopy(actual_list)

    def increase_flight(self, target_list: list, seed: int) -> list:
        """
        通过循环尝试将停靠间隔塞进去
        :return: interval list 能增加的停靠间隔
        """
        original_interval = copy.deepcopy(self.interval)
        ref_original_interval = copy.deepcopy(self.interval)  # fixed

        # the mapping between the original interval and the ref_original_interval
        mapping = {ref_original_interval[i]: (original_interval[i], ref_original_interval[i]) for i in
                   range(len(ref_original_interval))}

        n = len(self.interval)  # the number of original flights

        random.seed(seed)  # 随机种子

        increase_list = []

        while len(increase_list) < n * self.rate:
            random_index = random.randint(0, len(original_interval) - 1)
            inst = original_interval[random_index]

            # 如果inst的target时间在一个小时内，不增加
            # 注意: 对于neighbor同样考虑这个问题 详情可见 self._get_neighbor_flight(...) 函数
            if judge_inst_in_one_hour(inst):
                original_interval.remove(inst)
                continue

            # find the index of the inst in the original_interval(delete)
            idx = original_interval.index(inst)

            # find the index of the inst in the ref_original_interval(keep)
            ref_idx = None
            for index, _ in enumerate(ref_original_interval):
                if inst is mapping[ref_original_interval[index]][0]:
                    ref_idx = index
                    break

            original_interval.remove(inst)

            # add the neighbor flight(if available) and the new inst
            add_list = self._get_neighbor_flight(inst, idx, ref_idx, original_interval, ref_original_interval)

            # consider turbulence
            add_list = delay_time(add_list, self.interval, "ALDT")

            # find_suitable_gate again
            add_list = find_suitable_gate_total(add_list, self.interval)

            # 校验他是否在actual_interval_list里面也能增加
            add_list, ref_list = judge_in_actual(add_list, target_list)
            target_list.extend(ref_list)

            increase_list.extend(add_list)
            self.interval.extend(add_list)

            if len(original_interval) == 0:
                break
        return increase_list

    @loguru.logger.catch
    def _get_neighbor_flight(self, inst: IntervalBase, idx: int, ref_idx: int, original_interval: list,
                             ref_original_interval: list) -> list:
        if inst.begin_callsign != inst.end_callsign:
            return [inst]

        # find another inst before(de) or after(ar) the inst
        # if the inst and the inst_neighbor have the same registration, find another gate for the inst_neighbor
        inst_type = inst.begin_callsign[-2:].rstrip()

        min_inst, max_inst = self._get_index_range(inst, ref_idx, ref_original_interval)

        # the inst is at the beginning or the end of the group, it has no neighbor
        if inst_type == "de" and min_inst.begin_interval == inst.begin_interval:
            return [inst]
        if inst_type == "ar" and max_inst.begin_interval == inst.begin_interval:
            return [inst]

        # the first flight of instances is departure, and it is not the first one of the group
        if inst_type == "de" and idx == 0:
            return []

        # the last flight of instances is arrival, and it is not the last one of the group
        if inst_type == "ar" and idx == len(original_interval):
            return []

        inst_neighbor = original_interval[idx - 1] if inst_type == "de" else original_interval[idx]

        # 去掉通过neighbor找到的target时间在一小时之内的航班
        if judge_inst_in_one_hour(inst_neighbor):
            original_interval.remove(inst_neighbor)
            return [inst]

        # the inst is in the middle of the group, it has no neighbor
        if inst.registration != inst_neighbor.registration:
            return []

        inst_neighbor_type = inst_neighbor.begin_callsign[-2:].rstrip()
        # Dealing with extreme scenarios:
        # before this iteration, the inst in the middle has already been deleted, like(de ar de) => (de de)
        # In this iteration, one of the "de" has been chosen.
        # We deleted it and remain the other one.
        if inst_neighbor_type == inst_type:
            return []

        original_interval.remove(inst_neighbor)

        # the inst_neighbor has a suitable gate
        # 防止数据污染
        return [copy.deepcopy(inst), copy.deepcopy(inst_neighbor)]

    def _get_index_range(self, new_inst: IntervalBase, ref_idx: int, ref_original_interval: list) -> tuple:
        min_inst = self._get_min_idx(new_inst, ref_idx, ref_original_interval)
        max_inst = self._get_max_idx(new_inst, ref_idx, ref_original_interval)
        return min_inst, max_inst

    def _get_min_idx(self, new_inst: IntervalBase, ref_idx: int, ref_original_interval: list) -> IntervalBase:
        # the first instances of the group
        min_idx = ref_idx - 1
        if min_idx < 0:
            return ref_original_interval[0]
        next_inst = ref_original_interval[min_idx]
        if new_inst.registration == next_inst.registration and min_idx > 0:
            return self._get_min_idx(new_inst, min_idx, ref_original_interval)
        return ref_original_interval[min_idx + 1]

    def _get_max_idx(self, new_inst: IntervalBase, ref_idx: int, ref_original_interval: list) -> IntervalBase:
        # the last instances of the group
        max_idx = ref_idx + 1
        if max_idx >= len(ref_original_interval):
            return ref_original_interval[-1]
        next_inst = ref_original_interval[max_idx]
        if new_inst.registration == next_inst.registration and max_idx < (len(ref_original_interval) - 1):
            return self._get_max_idx(new_inst, max_idx, ref_original_interval)
        return ref_original_interval[max_idx - 1]
