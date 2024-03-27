import pandas as pd


def get_all_taxiing_time() -> dict:
    """
    从“E:/pycharm/GAP/data/mintaxitime.xlsx”获取每个停机坪对应的滑行时间
    """
    data = pd.read_excel("../data/mintaxitime.xlsx", sheet_name=None, header=2)
    data = data["mintaxitime"].to_dict(orient="list")

    real_data = {}

    error_key = list(data.keys())[0]

    for ev in data[error_key]:
        ev_list = ev.split(" ")
        real_data[ev_list[0]] = {
            "MANEX": {
                "DEP-16R": int(ev_list[1]),
                "ARR-16L": int(ev_list[2]),
                "ARR-16R": int(ev_list[3])
            },
            "MIN": {
                "DEP-16R": int(ev_list[4]),
                "ARR-16L": int(ev_list[5]),
                "ARR-16R": int(ev_list[6])
            },
            "PN_MANEX": {
                "DEP-16R": int(ev_list[7]),
                "ARR-16L": int(ev_list[8]),
                "ARR-16R": int(ev_list[9])
            },
            "PN_MIN": {
                "DEP-16R": int(ev_list[10]),
                "ARR-16L": int(ev_list[11]),
                "ARR-16R": int(ev_list[12])
            }
        }
    return real_data


class GetTaxiingTime:
    taxiing_file_data = get_all_taxiing_time()

    def __init__(self, gate: str, pattern: str):
        self.gate = gate
        self.pattern = pattern
        self.taxiing_time = self.get_taxiing_time()

    def get_taxiing_time(self):
        """
        获取当前停机坪的滑行时间
        """
        return GetTaxiingTime.taxiing_file_data[self.gate][self.pattern]


if __name__ == '__main__':
    get_all_taxiing_time()
