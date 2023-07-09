
def taxiingtime_matrix(taxiingtime, interval_data, interval_pattern):
    n = len(interval_data['interval'])
    m = len(taxiingtime.keys())
    gate = list(taxiingtime.keys())
    # print(gate)
    matrix = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            if interval_pattern[i][0] == 0:
                matrix[i][j] = matrix[i][j] + 0
            else:
                matrix[i][j] = matrix[i][j] + taxiingtime[gate[j]][interval_pattern[i][0]-1]
            if interval_pattern[i][1] == 0:
                matrix[i][j] = matrix[i][j] + 0
            else:
                matrix[i][j] = matrix[i][j] + taxiingtime[gate[j]][interval_pattern[i][1] - 1]
    return matrix
