import datetime
import tle_functions
import yaml
import yaml_reader
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from StateVector import StateVector
from pygeodesy.ellipsoidalKarney import Cartesian
from pygeodesy.ellipsoidalKarney import LatLon
import copy

# open the yaml file and load it
opened = open('FUNcube.yml', 'r')
loaded = yaml.load(opened)
tle = yaml_reader.extractTLE(loaded)
line1 = yaml_reader.extractLine1(loaded)
line2 = yaml_reader.extractLine2(loaded)
startRecord = yaml_reader.extractStartRecordTime(loaded)
endRecord = yaml_reader.extractEndRecordTime(loaded)

vernalEquinox = datetime.datetime(2018, 3, 20, 17, 15, 0, 0)
ut1 = 86164.090530

doptrack = LatLon(51.99888889, 4.37333333, height=134.64, name='DopTrackStation').toCartesian()
# From http://www.apsalin.com/convert-geodetic-to-cartesian.aspx :
dopStateVec = StateVector(3923683.03350176 / 1000, 300074.043717263 / 1000, 5002833.32624071 / 1000, 0,0,0)
satellite = twoline2rv(line1, line2, wgs72)

def getStateVectors(starttime, endtime, delta_seconds):
    state_vecs = []
    currenttime = starttime

    while (currenttime < endtime):
        pos, vel = satellite.propagate(currenttime.year, currenttime.month, currenttime.day, currenttime.hour,
                                            currenttime.minute, currenttime.second)
        state_vec = StateVector(pos[0], pos[1], pos[2], vel[0], vel[1], vel[2])
        state_vec.rotate_time(currenttime)
        state_vecs.append(state_vec)

        currenttime = currenttime + datetime.timedelta(0, delta_seconds)
    return state_vecs

def getDoptrackVec(starttime, endtime, delta_seconds):
    doptrack_vectors = []
    current_time = starttime

    while (current_time < endtime):
        doptrack_vec = StateVector(doptrack.x/1000, doptrack.y/1000, doptrack.z/1000, 0, 0, 0)
        doptrack_vec.rotate_time(current_time)
        doptrack_vectors.append(doptrack_vec)

        current_time = current_time + datetime.timedelta(0, delta_seconds)
    return doptrack_vectors

def getRotatedDopVecs(start_time, end_time, delta_seconds):
    doptrack_vectors = []
    current_time = start_time

    while (current_time < end_time):
        dop_vec = copy.copy(dopStateVec)
        dop_vec.rotate_time(current_time)
        doptrack_vectors.append(dop_vec)

        current_time = current_time + datetime.timedelta(0, delta_seconds)
    return doptrack_vectors

state_vectors = getStateVectors(startRecord, endRecord, 10)
doptrack_vectors = getRotatedDopVecs(startRecord, endRecord, 10) #getDoptrackVec(startRecord, endRecord, 10)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

xs_sat = list(map(lambda x: x.posX(), state_vectors))
ys_sat = list(map(lambda x: x.posY(), state_vectors))
zs_sat = list(map(lambda x: x.posZ(), state_vectors))
# ax.scatter(xs_sat, ys_sat, zs_sat)

xs_doptrack = list(map(lambda x: x.posX(), doptrack_vectors))
ys_doptrack = list(map(lambda x: x.posY(), doptrack_vectors))
zs_doptrack = list(map(lambda x: x.posZ(), doptrack_vectors))
ax.scatter(xs_doptrack, ys_doptrack, zs_doptrack)


ellipsoid = []

for lat in range(18):
    for lon in range (36):
        point = LatLon((lat*10) - 90, (lon*10) - 180)
        ellipsoid.append(point.toCartesian())

xs_earth = list(map(lambda x: x.x/1000, ellipsoid))
ys_earth = list(map(lambda x: x.y/1000, ellipsoid))
zs_earth = list(map(lambda x: x.z/1000, ellipsoid))

# Plot the earth
# ax.scatter(xs_earth, ys_earth, zs_earth, color='r')

prime_meridian_vernal_equinox = []
prime_meridian_at_start = []

for lat in range (18):
    point_cartesian = LatLon((lat*10) - 90, 0).toCartesian()
    point = StateVector(point_cartesian.x/1000, point_cartesian.y/1000, point_cartesian.z/1000,0,0,0)
    prime_meridian_vernal_equinox.append(point)
    point_ = StateVector(point_cartesian.x/1000, point_cartesian.y/1000, point_cartesian.z/1000,0,0,0)
    point_.rotate_time(startRecord)
    prime_meridian_at_start.append(point_)

xs_prime = list(map(lambda x: x.posX(), prime_meridian_vernal_equinox))
ys_prime = list(map(lambda x: x.posY(), prime_meridian_vernal_equinox))
zs_prime = list(map(lambda x: x.posZ(), prime_meridian_vernal_equinox))
ax.scatter(xs_prime, ys_prime, zs_prime, color='g')

xs_prime_at_start = list(map(lambda x: x.posX(), prime_meridian_at_start))
ys_prime_at_start = list(map(lambda x: x.posY(), prime_meridian_at_start))
zs_prime_at_start = list(map(lambda x: x.posZ(), prime_meridian_at_start))
ax.scatter(xs_prime_at_start, ys_prime_at_start, zs_prime_at_start, color='y')


Axes3D.plot(ax, xs=[0,6000], ys=[0,0], zs=[0,0], c='r')
Axes3D.plot(ax, xs=[0,0], ys=[0,6000], zs=[0,0], c='g')
Axes3D.plot(ax, xs=[0,0], ys=[0,0], zs=[0,6000], c='b')

unit_vectors = []

for i in range(len(state_vectors)):
    # vec_to_dop = doptrack_vectors[i].minus(state_vectors[i])
    vec_to_dop = state_vectors[i].minus(doptrack_vectors[i])
    length = np.sqrt(np.square(vec_to_dop.posX()) + np.square(vec_to_dop.posY()) + np.square(vec_to_dop.posZ()))
    unit_v_t_d = StateVector(vec_to_dop.posX()/length, vec_to_dop.posY()/length, vec_to_dop.posZ()/length, 0, 0, 0)
    unit_vectors.append(unit_v_t_d)

range_rates = []

for i in range(len(unit_vectors)):
    cur_unit = unit_vectors[i]
    cur_vel = state_vectors[i]
    # range_rate = StateVector(cur_unit.posX()*cur_vel.velX(), cur_unit.posY()*cur_vel.velY(), cur_unit.posZ()*cur_vel.velZ(),0,0,0)
    range_rate = cur_unit.times(cur_unit.dotPosVel(cur_vel))
    range_rate.printLength()
    range_rates.append(range_rate)

for i in range(len(state_vectors)):
    # Sat to doptrack
    # Axes3D.plot(ax, xs=[state_vectors[i].posX(), doptrack_vectors[i].posX()],
    #             ys=[state_vectors[i].posY(), doptrack_vectors[i].posY()],
    #             zs=[state_vectors[i].posZ(), doptrack_vectors[i].posZ()], c='c')

    #Sat + unit
    # Axes3D.plot(ax, xs=[state_vectors[i].posX(), state_vectors[i].posX() + unit_vectors[i].posX()],
    #             ys=[state_vectors[i].posY(), state_vectors[i].posY() + unit_vectors[i].posY()],
    #             zs=[state_vectors[i].posZ(), state_vectors[i].posZ() + unit_vectors[i].posZ()])

    #Sat + rangerate
    Axes3D.plot(ax, xs=[state_vectors[i].posX(), state_vectors[i].posX() + range_rates[i].posX()],
                ys=[state_vectors[i].posY(), state_vectors[i].posY() + range_rates[i].posY()],
                zs=[state_vectors[i].posZ(), state_vectors[i].posZ() + range_rates[i].posZ()])


    # Sat to center of earth
    # Axes3D.plot(ax, xs=[state_vectors[i].posX(), 0],
    #             ys=[state_vectors[i].posY(), 0],
    #             zs=[state_vectors[i].posZ(), 0], c='m')

    # Doptrack to center of earth
    Axes3D.plot(ax, xs=[0, doptrack_vectors[i].posX()],
                ys=[0, doptrack_vectors[i].posY()],
                zs=[0, doptrack_vectors[i].posZ()])

plt.show()

