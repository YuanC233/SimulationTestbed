import numpy as np
import pandas as pd
import random
from matplotlib import pyplot as plt
random.seed(1)

'''
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

'''

def generate_schedule(file, days):
    schedule = pd.read_csv(file)
    full_schedule = pd.read_csv(file)
    for i in range(days):
        full_schedule = full_schedule.append(schedule, ignore_index=True)
    return full_schedule


def generate_load_comparison_plot(HVAC_load, non_HVAC_load, step):
    HVAC = pd.read_csv(HVAC_load)
    non_HVAC = pd.read_csv(non_HVAC_load)
    HVAC_zone1 = HVAC.iloc[:step, 1]
    non_HVAC_zone1 = non_HVAC.iloc[:step, 2]

    x = range(step)

    # stacked area plot for zone1
    # Basic stacked area chart.
    plt.stackplot(x, HVAC_zone1, non_HVAC_zone1, labels=['Zone1_HVAC', 'Zone1_nonHVAC'])
    plt.legend(loc='upper left')
    plt.show()


def generate_load_decomposition(T, t, s, i, e, step):
    Tout = pd.read_csv(T)
    total = pd.read_csv(t)
    solar = pd.read_csv(s)
    internal = pd.read_csv(i)
    equipment = pd.read_csv(e)
    To = Tout.iloc[:step, 1]
    solar_load = (solar.iloc[:step, 1] + solar.iloc[:step, 2] + solar.iloc[:step, 3] + solar.iloc[:step, 4])*5/1000/3
    internal_load = internal.iloc[:step, 2] + internal.iloc[:step, 4] + internal.iloc[:step, 6] + internal.iloc[:step, 8] + internal.iloc[:step, 10]
    equipment_load = equipment.iloc[:step, 1]*200
    conductive = total.iloc[:step, 1] - equipment_load - internal_load - solar_load

    x = range(step)

    print('solar', solar_load[48: 72])
    print('internal', internal_load[48: 72])
    print('equipment', equipment_load[48: 72])
    print('conductive', conductive[48: 72])

    plt.stackplot(x, solar_load, internal_load, equipment_load, labels=['solar', 'internal', 'equipment'])
    plt.plot(x, conductive, x, To)
    plt.legend(loc='upper left')
    plt.show()


if __name__ == "__main__":
    #solar = generate_solar_radiation(92, 1000)
    #print(solar)
    #plt.figure()
    #plt.plot(solar[:, 0], solar[:, 1:])
    #plt.show()
    #solar_df = pd.DataFrame(solar, columns=['Time', 'South(Wh/m2)', 'West(Wh/m2)', 'East(Wh/m2)', 'North(Wh/m2)'])
    #print(solar_df)
    #solar_df.to_csv('Austin_Simulated_solar_4orientations.csv', index=False)

    #full_schedule = generate_schedule('Daily_Schedule.csv', 92)
    #print(full_schedule)
    #full_schedule.to_csv('Full_schedule.csv', index=False)

    #generate_load_comparison_plot('Testbed_HVAC_load_output.csv', 'Testbed_Full_schedule.csv', step=24*7)
    generate_load_decomposition('Austin_Tout_model_input.csv', 'FiveZone_total_load_1002.csv', 'Austin_solar_data_input.csv', 'Testbed_Full_schedule.csv', 'Cornell_Homer_electricity_sqm_consumption_1002.csv', step=24*3)
