import numpy as np
import pandas as pd
import random
from matplotlib import pyplot as plt
random.seed(1)

def generate_solar_radiation(days, peak):
    hours = 24 * days
    # create nd-array, 0: hour, 1: south, 2: west, 3: east, 4: north
    solar = np.zeros((hours, 5))
    for day in range(days):
        cloudiness = round(random.random(), 3)

        for hour in range(24):
            solar[(day-1)*24 + hour, 0] = hour
            # south facade:
            solar[(day-1)*24 + hour, 1] = max(-1./108*peak*(hour-6)*(hour-18), 0)*cloudiness*round(random.uniform(0.90, 1.10), 2)
            # west facade:
            if hour < 14:
                solar[(day-1)*24 + hour, 2] = max(1./12*peak*hour - 1./2*peak, 0)*cloudiness*round(random.uniform(0.90, 1.10), 2)
            else:
                solar[(day-1)*24 + hour, 2] = max(-1./6*peak*hour + 3*peak, 0)*cloudiness*round(random.uniform(0.90, 1.10), 2)
            # east facade:
            if hour < 10:
                solar[(day-1)*24 + hour, 3] = max(1./6*peak*hour - peak, 0)*cloudiness*round(random.uniform(0.90, 1.10), 2)
            else:
                solar[(day-1)*24 + hour, 3] = max(-1./12*peak*hour + 3./2*peak, 0)*cloudiness*round(random.uniform(0.90, 1.10), 2)
            # north facade:
            solar[(day-1)*24 + hour, 4] = max(-1./144*peak*(hour-6)*(hour-18), 0)*cloudiness*round(random.uniform(0.90, 1.10), 2)
    return solar

def generate_schedule(file, days):
    schedule = pd.read_csv(file)
    full_schedule = pd.read_csv(file)
    for i in range(days):
        full_schedule = full_schedule.append(schedule, ignore_index=True)
    return full_schedule


if __name__ == "__main__":
    #solar = generate_solar_radiation(92, 1000)
    #print(solar)
    #plt.figure()
    #plt.plot(solar[:, 0], solar[:, 1:])
    #plt.show()
    #solar_df = pd.DataFrame(solar, columns=['Time', 'South(Wh/m2)', 'West(Wh/m2)', 'East(Wh/m2)', 'North(Wh/m2)'])
    #print(solar_df)
    #solar_df.to_csv('Austin_Simulated_solar_4orientations.csv', index=False)

    full_schedule = generate_schedule('Test_Daily_Schedule.csv', 92)
    print(full_schedule)
    full_schedule.to_csv('Test_Full_schedule.csv', index=False)
