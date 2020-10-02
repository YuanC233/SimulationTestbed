from Zone import Zone
from Building import System
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

SIM_TIMESTEP = 24*3

# read zone parameters from csv file
zone_info = pd.read_csv('ZoneInfo.csv')
#print(zone_info)

# read zone schedule (Tset and Qall): as now, each zone has its own schedule
schedule = pd.read_csv('Testbed_Full_schedule.csv')
# schedule = pd.read_csv('Test_Full_schedule.csv')
#print(schedule)

# read solar radiation profile for 4 orientations
#solar_radiation = pd.read_csv('Simulated_solar_4orientations.csv')
solar_radiation = pd.read_csv('Austin_solar_data_input.csv')

# create zone object with zone_info
zone_dict = {}
for i in zone_info.index:
    ID = zone_info.iloc[i, 0]  # define zone id
    R = zone_info.iloc[i, 1]  # define zone R
    C = zone_info.iloc[i, 2]  # define zone C
    Tinit = zone_info.iloc[i, 3]  # define initial zone temperature
    Pmax = zone_info.iloc[i, 4]  # define zone Pmax
    COP = zone_info.iloc[i, 5]  # define zone COP
    orient = zone_info.iloc[i, 6]  # define zone orientation (wall/window)
    condition = zone_info.iloc[i, 7]  # define zone heating/cooling condition
    window_size = zone_info.iloc[i, 9]  # define effective window area
    Tset_schedule = schedule.iloc[:SIM_TIMESTEP, 2*i + 1]  # define zone specific setpoint temp schedule
    Qall_schedule = schedule.iloc[:SIM_TIMESTEP, 2*i + 2]  # define zone specific exogenous heat flow schedule
    neighborlist = [int(neib) for neib in zone_info.iloc[i, 8].strip().split(',')]  # define zone neighbor ids
    current_zone = Zone(ID=ID, R=R, C=C, Tinit=Tinit, Pmax=Pmax, COP=COP, orient=orient, condition=condition,
                        Tset_schedule=Tset_schedule, Qall_schedule=Qall_schedule, windowA=window_size, neighborlist=neighborlist)
    zone_dict[current_zone.ID] = current_zone  # add zone object to zone dict

# add zone objects to zone neighbors
for zone_obj in zone_dict.values():
    neighbors = [zone_dict[zone_id] for zone_id in zone_obj.neighborlist]
    zone_obj.add_neighbors(neighbors)
#print([i for i in zone_dict[1].get_neighbors()]) # get all neighbor ids

for zone_obj in zone_dict.values():
    if zone_obj.orient == 1:
        zone_obj.setup_solar_radiation_schedule(solar_radiation.iloc[:SIM_TIMESTEP, 1]*zone_obj.windowA/1000)
    elif zone_obj.orient == 2:
        zone_obj.setup_solar_radiation_schedule(solar_radiation.iloc[:SIM_TIMESTEP, 2]*zone_obj.windowA/1000)
    elif zone_obj.orient == 3:
        zone_obj.setup_solar_radiation_schedule(solar_radiation.iloc[:SIM_TIMESTEP, 3]*zone_obj.windowA/1000)
    elif zone_obj.orient == 4:
        zone_obj.setup_solar_radiation_schedule(solar_radiation.iloc[:SIM_TIMESTEP, 4]*zone_obj.windowA/1000)
    else:  # should be 0, internal zone
        zone_obj.setup_solar_radiation_schedule(solar_radiation.iloc[:SIM_TIMESTEP, 2] * zone_obj.windowA/1000)


# read outdoor temperature
# weather = pd.read_csv('Cornell_Tout_model_input.csv')
weather = pd.read_csv('Austin_Tout_model_input.csv')
#print(weather)

# initiate system
system1 = System()

# initiate system load and indoor temperature
system_HVAC_load = np.zeros((SIM_TIMESTEP, len(zone_dict)))
Tin = np.zeros((SIM_TIMESTEP, len(zone_dict)))

# main loop
for step in range(SIM_TIMESTEP):
    # at each timestep set zone Tset and Qall according to schedule
    for zone_obj in zone_dict.values():
        zone_obj.update_Qall(step)
        zone_obj.update_Tset(step)

    system1.update_zonelist(zone_dict.values())
    #print(zone_dict.values())

    # at each timestep update Tout to the system
    system1.update_Tout(weather.iloc[step, 1])

    #print(system1.get_A())
    #print(system1.get_B())
    #print(system1.get_W())
    current_load = system1.load_calculation(deltaT=1)
    #print(current_load)
    system_HVAC_load[step, :] = (current_load.squeeze()>=0)*current_load.squeeze()
    #system_HVAC_load[step, :] = current_load.squeeze()

    for zone in system1.zonelist:
        zone.update_P(system_HVAC_load[step, zone.ID-1])
        #print('zoneP',zone.ID, zone.P)

    #system1.update_zonelist(zone_dict.values())
    system1.update_all_zone_P()

    current_T = system1.discrete_systemT_update(deltaT=1)
    #print(current_T)
    Tin[step, :] = current_T.squeeze()
    for zone in system1.zonelist:
        zone.update_Tin(Tin[step, zone.ID-1])
        #print('zoneT',zone.Tin)
    #system1.update_zonelist(zone_dict.values())
    system1.update_all_zone_Tin()
#print(system_HVAC_load)

x = range(0, SIM_TIMESTEP, 1)
plt.figure(figsize=(20, 8))
plt.plot(x, system_HVAC_load[:, 0], x, system_HVAC_load[:, 1], x, system_HVAC_load[:, 2], x, system_HVAC_load[:, 3],
x, system_HVAC_load[:, 4])
plt.xlabel('Time of the day(hour)')
plt.ylabel('HVAC Load (kW)')
plt.legend(['Zone1: south', 'Zone2: west', 'Zone3: east', 'Zone4: north', 'Zone5: interior'])
plt.show()

plt.figure(figsize=(20, 8))
plt.plot(x, schedule.iloc[:SIM_TIMESTEP, [2, 4, 6, 8, 10]])
plt.xlabel('Time of the day(hour)')
plt.ylabel('Exog Q (kW)')
plt.legend(['Zone1', 'Zone2', 'Zone3', 'Zone4', 'Zone5'])
plt.show()

plt.figure(figsize=(20, 8))
plt.plot(x, schedule.iloc[:SIM_TIMESTEP, [1, 3, 5, 7, 9]], x, weather.iloc[:SIM_TIMESTEP, 1])
plt.xlabel('Time of the day(hour)')
plt.ylabel('Setpoint Temp (C)')
plt.legend(['Zone1', 'Zone2', 'Zone3', 'Zone4', 'Zone5', 'Tout'])
plt.show()

plt.figure(figsize=(20, 8))
plt.plot(x, Tin[:, 0], x, Tin[:, 1], x, Tin[:, 2], x, Tin[:, 3], Tin[:, 4])
plt.xlabel('Time of the day (hour)')
plt.ylabel('Room Temp (C)')
plt.legend(['Zone1', 'Zone2', 'Zone3', 'Zone4', 'Zone5'])
plt.show()


fig, ax1 = plt.subplots()
color = 'tab:red'
ax1.set_xlabel('Time of the day (hour)')
ax1.set_ylabel('Temp (C)')
ax1.plot(x, Tin[:, 0], x, schedule.iloc[:SIM_TIMESTEP, 1], color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax1.legend(['Tin', 'Setpoint Temp'])

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Load', color=color)  # we already handled the x-label with ax1
ax2.plot(x, schedule.iloc[:SIM_TIMESTEP, 2], x, system_HVAC_load[:, 0], color=color)
ax2.tick_params(axis='y', labelcolor=color)
ax2.legend(['Q exog', 'HVAC load'])

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()

system_load = pd.DataFrame(system_HVAC_load)
print(system_load)
print(type(system_load))
#system_load.to_csv('Testbed_HVAC_load_output_1002.csv', index=False)
#print(Tin)