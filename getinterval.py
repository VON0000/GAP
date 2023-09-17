import numpy as np


class GetInterval:
    @staticmethod
    def actual_target(data, quarter):
        """

        Every 15 minutes, replace the target time with the actual time before the current moment.
        """
        departure = np.array(data['departure'])
        departure_set = np.where(departure == 'ZBTJ')[0]
        h = 60 * 60
        q = 15 * 60
        n = len(data['data'])
        tot = data['TTOT']
        ldt = data['TLDT']
        for i in range(n):
            if i in departure_set:
                if data['ATOT'][i] <= quarter * q + h:
                    tot[i] = data['ATOT'][i]
                else:
                    if data['TTOT'][i] < quarter * q:
                        tot[i] = data['ATOT'][i]
            else:
                if data['ALDT'][i] <= quarter * q + h:
                    ldt[i] = data['ALDT'][i]
                else:
                    if data['TLDT'][i] < quarter * q:
                        ldt[i] = data['ALDT'][i]
        return tot, ldt

    @staticmethod
    def longtime_arrivee(i, ldt):
        m = 60
        begin_interval = ldt[i] + 10 * m
        end_interval = ldt[i] + 30 * m
        interval = end_interval - begin_interval
        return interval, begin_interval, end_interval

    @staticmethod
    def longtime_departure(i, tot):
        m = 60
        begin_interval = tot[i] - 30 * m
        end_interval = tot[i] - 10 * m
        interval = end_interval - begin_interval
        return interval, begin_interval, end_interval

    @staticmethod
    def shorttime(i, ldt, tot, sorted_indices):
        m = 60
        begin_interval = ldt[sorted_indices[i]] + 10 * m
        end_interval = tot[sorted_indices[i + 1]] - 10 * m
        interval = end_interval - begin_interval
        return interval, begin_interval, end_interval

    @staticmethod
    def interval_value(data, i, sorted_indices, interval_data, temp):
        interval_data['interval'].append(temp[0])
        interval_data['begin_interval'].append(temp[1])
        interval_data['end_interval'].append(temp[2])
        interval_data['airline'].append(data['Airline'][sorted_indices[i]])
        interval_data['registration'].append(data['registration'][sorted_indices[i]])
        interval_data['begin_callsign'].append(data['callsign'][sorted_indices[i]])
        interval_data['end_callsign'].append(data['callsign'][sorted_indices[i]])
        interval_data['wingspan'].append(data['Wingspan'][sorted_indices[i]])
        # print(interval_data['begin_interval'])
        return interval_data

    def get_interval(self, data, departure_set, num, pattern, tot, ldt):
        """

        Get the parking interval for each aircraft
        """
        zbtj_time = []
        for i in num:
            if i in departure_set:
                zbtj_time.append(tot[i])
            else:
                zbtj_time.append(ldt[i])
        sorted_indices = [i for i, _ in sorted(enumerate(zbtj_time), key=lambda x: x[1])]
        # print(zbtj_time)
        sorted_indices = sorted_indices + num[0]
        # print(sorted_indices)
        h = 60 * 60
        i = 0
        my_key = ['interval', 'begin_interval', 'end_interval', 'airline', 'registration', 'begin_callsign',
                  'end_callsign', 'wingspan']
        my_values = [[], [], [], [], [], [], [], []]
        interval_data = {k: v for k, v in zip(my_key, my_values)}
        interval_pattern = []
        interval_flight = []
        while i < len(sorted_indices):
            if sorted_indices[i] in departure_set:
                temp = self.longtime_departure(i, tot)
                interval_data = self.interval_value(data, i, sorted_indices, interval_data, temp)
                interval_pattern.append([0, pattern[sorted_indices[i]]])
                interval_flight.append([sorted_indices[i]])
                # print(interval_data)
                i = i + 1
            else:
                if i + 1 < len(sorted_indices):
                    arrivee_time = ldt[sorted_indices[i]]
                    departure_time = tot[sorted_indices[i + 1]]
                    interval_time = departure_time - arrivee_time
                    # print(interval_time)
                    if interval_time <= h:
                        if interval_time >= h * 2 / 3:
                            temp = self.shorttime(i, ldt, tot, sorted_indices)
                            interval_data = self.interval_value(data, i, sorted_indices, interval_data, temp)
                            # print(interval_data)
                            interval_pattern.append([pattern[sorted_indices[i]], pattern[sorted_indices[i+1]]])
                            interval_flight.append([sorted_indices[i], sorted_indices[i + 1]])
                        else:
                            temp = self.longtime_arrivee(i, ldt)
                            interval_data = self.interval_value(data, i, sorted_indices, interval_data, temp)
                            interval_pattern.append([pattern[sorted_indices[i]], 0])
                            interval_flight.append([sorted_indices[i]])
                    else:
                        temp = self.longtime_arrivee(i, ldt)
                        interval_data = self.interval_value(data, i, sorted_indices, interval_data, temp)
                        temp = self.longtime_departure(i + 1, tot)
                        interval_data = self.interval_value(data, i + 1, sorted_indices, interval_data, temp)
                        interval_pattern.append([pattern[sorted_indices[i]], 0])
                        interval_pattern.append([0, pattern[sorted_indices[i + 1]]])
                        interval_flight.append([sorted_indices[i]])
                        interval_flight.append([sorted_indices[i + 1]])
                        # print(interval_data)
                else:
                    temp = self.longtime_arrivee(i, ldt)
                    interval_data = self.interval_value(data, i, sorted_indices, interval_data, temp)
                    interval_pattern.append([pattern[sorted_indices[i]], 0])
                    interval_flight.append([sorted_indices[i]])
                    # print(interval_data)
                i = i + 2
        # print(interval_data)
        return interval_data, interval_pattern, interval_flight

    def presolve(self, quarter, data, seuil, delta):
        """

        Get all parking intervals
        """
        temp = self.actual_target(data, quarter)
        tot = temp[0]
        ldt = temp[1]
        pattern = self.taxiing_pattern(quarter, seuil, data)
        n = len(data['data'])
        departure_set = []
        for i in range(0, n):
            if data['departure'][i] == 'ZBTJ':
                departure_set.append(i)
        # print(departure_set)
        my_key = ['interval', 'begin_interval', 'end_interval', 'airline', 'registration', 'begin_callsign',
                  'end_callsign', 'wingspan']
        default_value = []
        interval_data = dict.fromkeys(my_key, default_value)
        interval_pattern = []
        interval_flight = []
        sample = []
        for i in range(n):
            registration = np.array(data['registration'])
            temp = np.where(registration == data['registration'][i])
            num = list(temp[0])
            num.sort()
            # print(num, i)
            if not np.array_equal(sample, num):
                temp_interval = self.get_interval(data, departure_set, num, pattern, tot, ldt)
                temp_interval_data = temp_interval[0]
                temp_interval_pattern = temp_interval[1]
                temp_interval_flight = temp_interval[2]
                interval_data = {key: interval_data[key] + temp_interval_data[key] for key in interval_data}
                interval_pattern.extend(temp_interval_pattern)
                interval_flight.extend(temp_interval_flight)
                sample = num
        delete_set = ([i for i, val in enumerate(interval_data['begin_interval']) if int(val) >= 86400])
        for key in interval_data:
            interval_data[key] = [interval_data[key][i] for i in range(len(interval_data[key])) if i not in delete_set]
        # print(interval_data)
        interval_pattern = [interval_pattern[i] for i in range(len(interval_pattern)) if i not in delete_set]
        interval_flight = [interval_flight[i] for i in range(len(interval_flight)) if i not in delete_set]
        # print(interval_pattern)
        minute = 60
        for i in range(len(interval_pattern)):
            if interval_pattern[i][1] == 1:
                interval_data['end_interval'][i] = interval_data['end_interval'][i] + minute * delta
        return interval_data, interval_pattern, interval_flight, pattern

    def taxiing_pattern(self, quarter, seuil, data):
        """

        Choose 16R or 16L for each aircraft
        """
        # 1 dep_16R 2 arr_16L 3 dep_16R
        temp = self.actual_target(data, quarter)
        tot = temp[0]
        ldt = temp[1]
        n = len(data['data'])
        departure = data['departure']
        departure_set = []
        arrivee_set = []
        for i in range(len(departure)):
            if departure[i] == 'ZBTJ':
                departure_set.append(i)
            else:
                arrivee_set.append(i)
        # departure_set = np.where(departure == 'ZBTJ')[0]
        # arrivee_set = np.where(data['arrivee'] == 'ZBTJ')[0]
        departure_time = []
        arrivee_time = []
        for i in range(n):
            if i in departure_set:
                departure_time.append(int(tot[i]))
            else:
                arrivee_time.append(int(ldt[i]))
        h = 60 * 60
        pattern = [0] * n
        # print(departure_set)
        for i in departure_set:
            pattern[i] = 1
        for i in range(24):
            departure_index = [index for index, x in enumerate(departure_time) if h * i < x <= (h * (i + 1))]
            arrivee_index = [index for index, x in enumerate(arrivee_time) if h * i < x <= (h * (i + 1))]
            amount = len(departure_index) + len(arrivee_index)
            for index in arrivee_index:
                if amount < seuil:
                    pattern[arrivee_set[index]] = 3
                else:
                    pattern[arrivee_set[index]] = 2
        # print(pattern)
        return pattern
