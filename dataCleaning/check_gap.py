import os
import re

APT = "ZBTJ"
TAXI_D = 5
GATE_D = 10


class Mvt:
    def __init__(self, line):
        fields = line.strip().split(",")
        date, callsign, orig, dest = fields[:4]
        atot, aldt = (int(sec) // 60 for sec in fields[6:8])
        typ, wingspan, airline, qfu, gate, registration = fields[8:14]
        self.callsign = callsign
        self.dep = orig == APT
        self.gate = gate
        self.gate_t = atot - TAXI_D - GATE_D if self.dep else aldt + TAXI_D
        self.rwy_t = atot if self.dep else aldt

    def __repr__(self):
        typ, t = ("DEP", "ATOT") if self.dep else ("ARR", "ALDT")
        return f"{typ} {self.callsign} {t}={hm(self.rwy_t)}"


def hm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def check_gap(file, gate_d=GATE_D):
    occ = {}
    print("check gap", file)
    with open(file) as f_in:
        title = f_in.readline()
        for line in f_in:
            mvt = Mvt(line)
            occ.setdefault(mvt.gate, []).append(mvt)
    for gate in sorted(occ):
        last = None
        for cur in sorted(occ[gate], key=lambda mvt: mvt.gate_t):
            if last and cur.gate_t < last.gate_t + gate_d:
                print(gate, last, "<->", cur)
            last = cur


folder_path = "../results/intermediateFile/t_a_total/re_concatenated_0.5"

for filename in os.listdir(folder_path):
    match = re.search(r"process", filename, re.M | re.I)
    if match is None and filename.endswith(".csv"):
        filename = os.path.join(folder_path, filename)
        check_gap(filename)
# for file in sys.argv[1:]:
#     check_gap(file)
