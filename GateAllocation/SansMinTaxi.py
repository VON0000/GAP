def delete_taxiing_time(taxiingtime: dict) -> dict:
    for key in taxiingtime.keys():
        n = len(taxiingtime[key])
        taxiingtime[key] = [0] * n
    return taxiingtime
