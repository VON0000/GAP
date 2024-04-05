from BasicFunction.AirlineType import AirlineType
from BasicFunction.GetGateAttribute import GetGateAttribute
from BasicFunction.IntervalType import IntervalBase
from GateAllocation.RemoteGate import REMOTE_GATE


def get_available_gate_GAP(inst: IntervalBase) -> list:
    if AirlineType(inst.airline).type == "domestic":
        available_gate_list = list(set(AirlineType(inst.airline).available_gate) | set(REMOTE_GATE))
    else:
        available_gate_list = AirlineType(inst.airline).available_gate

    available_gate_list = [g for g in available_gate_list if inst.wingspan <= GetGateAttribute(g).size]

    return available_gate_list


def get_available_gate_FIGAP(inst: IntervalBase) -> list:
    if AirlineType(inst.airline).type == "domestic":
        available_gate_list = list(set(AirlineType(inst.airline).get_type_gate()) | set(REMOTE_GATE))
    else:
        available_gate_list = AirlineType(inst.airline).available_gate

    available_gate_list = [g for g in available_gate_list if inst.wingspan <= GetGateAttribute(g).size]

    return available_gate_list
