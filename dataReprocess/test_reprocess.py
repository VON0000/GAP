from dataReprocess.calcuate_average_taxi_time import get_taxi_time, calculate_one_file


def test_calculate_one_file():
    mock_path = "../data/mock_240325.csv"

    taxi_time = get_taxi_time()

    switch = "MANEX"

    judge = [340, 450, 435, 410, 380, 405, 385, 400, 285, 635, 295, 500, 295, 360, 465, 380, 470, 385, 480]

    assert calculate_one_file(mock_path, taxi_time, switch) == sum(judge) / len(judge)

    switch = "PN_MANEX"

    judge = [340, 450, 435, 410, 380, 405, 385, 400, 285, 645, 295, 500, 295, 360, 465, 380, 470, 385, 480]

    assert calculate_one_file(mock_path, taxi_time, switch) == sum(judge) / len(judge)
