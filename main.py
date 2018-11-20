import datetime
import tle_functions
import yaml
import yaml_reader
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# open the yaml file and load it
opened = open('FUNcube.yml', 'r')
loaded = yaml.load(opened)
tle = yaml_reader.extractTLE(loaded)
line1 = yaml_reader.extractLine1(loaded)
line2 = yaml_reader.extractLine2(loaded)
startRecord = yaml_reader.extractStartRecordTime(loaded)
endRecord = yaml_reader.extractEndRecordTime(loaded)

satellite = twoline2rv(line1, line2, wgs72)

positions = []
velocities = []

currenttime = startRecord
while currenttime < endRecord:
    position, velocity = satellite.propagate(currenttime.year, currenttime.month, currenttime.day, currenttime.hour, 
                                            currenttime.minute, currenttime.second)
    # Add x seconds to the currenttime
    deltaSeconds = 10
    currenttime = currenttime + datetime.timedelta(0, deltaSeconds)
    positions.append(position)
    velocities.append(velocity)


# for x in range(0, 150):
#     position, velocity = satellite.propagate(startRecord.year, startRecord.month, startRecord.day, startRecord.hour,
#                                              startRecord.minute + x, startRecord.second)
#     positions.append(position)
#     velocities.append(velocity)

# print(positions)
# print(tle_functions.getInclination(tle))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

xs = list(map(lambda x: x[0], positions))
ys = list(map(lambda x: x[1], positions))
zs = list(map(lambda x: x[2], positions))

ax.scatter(xs, ys, zs)
plt.show()
# Axes3D.scatter(xs, ys, zs)