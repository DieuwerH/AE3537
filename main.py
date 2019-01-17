import datetime
import pytz
import tle_functions
import PlotHelper
import yaml
from yaml_reader import YamlReader
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
from mpl_toolkits.mplot3d import Axes3D
from StateVector import StateVector
from pygeodesy.ellipsoidalKarney import Cartesian
from pygeodesy.ellipsoidalKarney import LatLon
import copy

# open the yaml file and load it
opened = open('FUNcube-1_39444_201808311030.yml', 'r')
loaded = yaml.load(opened)
yml = YamlReader('FUNcube-1_39444_201808311030')
tle = yml.tle()
line1 = yml.line1()
line2 = yml.line2()
startRecord = yml.start_record_time()
endRecord = yml.end_record_time()
tuning_freq = yml.tuningfrequency()

# From http://www.apsalin.com/convert-geodetic-to-cartesian.aspx :
centerEarth = StateVector(0, 0, 0, 0, 0, 0)
doptrack = StateVector(3923683.03350176, 300074.043717263, 5002833.32624071, 0, 0, 0)
satellite = twoline2rv(line1, line2, wgs72)

c = 299792458 #m/s

def getStateVectors(starttime, endtime, delta_seconds):
    state_vecs = []
    current_time = starttime
    # endtime = endtime + datetime.timedelta(hours=1)

    while current_time < endtime:
        pos, vel = satellite.propagate(current_time.year, current_time.month, current_time.day, current_time.hour,
                                       current_time.minute, current_time.second)
        state_vec = StateVector(pos[0]*1000, pos[1]*1000, pos[2]*1000,
                                vel[0]*1000, vel[1]*1000, vel[2]*1000)
        state_vec.rotate_time(current_time)
        state_vecs.append(state_vec)

        current_time = current_time + datetime.timedelta(0, delta_seconds)
    return state_vecs


def getEarthPoints():
    ellipsoid = []
    for lat in range(18):
        for lon in range(36):
            point = LatLon((lat * 10) - 90, (lon * 10) - 180).toCartesian()
            point = StateVector(point.x, point.y, point.z, 0, 0, 0)
            ellipsoid.append(point)
    return ellipsoid


def getPrimeMeridian():
    prime_meridian_vernal_equinox = []
    for lat in range(18):
        point_cartesian = LatLon((lat * 10) - 90, 0).toCartesian()
        point = StateVector(point_cartesian.x, point_cartesian.y, point_cartesian.z, 0, 0, 0)
        prime_meridian_vernal_equinox.append(point)
    return prime_meridian_vernal_equinox


def getUnitVectors(state_vectors, dop_vec):
    unit_vectors = []

    for sat in state_vectors:
        # sat_to_dop = dop_vec.minus(sat)
        dop_to_sat = sat.minus(dop_vec)
        length = dop_to_sat.getRange()
        unit_s_t_d = dop_to_sat.divide(length)
        unit_vectors.append(unit_s_t_d)

    return unit_vectors


def getRangeRates(state_vectors, unit_vectors):
    range_rates = []

    for cur_unit, cur_vel in zip(unit_vectors, state_vectors):
        range_rate = cur_unit.times(cur_unit.dotPosVel(cur_vel))
        range_rates.append(range_rate)

    return range_rates


def rangeRateTest(state_vectors, unit_vectors):
    rates = []
    for unit, vel in zip(unit_vectors, state_vectors):
        rates.append(unit.dotPosVel(vel))
    return rates

def freqTest(range_rates, f0):
    fs = []
    for range_rate in range_rates:
        f = (1 - (range_rate/c))*f0
        fs.append(f)
    return fs

def getFrequencies(range_rates, directions, f0):
    frequencies = []

    for range_rate, direction in zip(range_rates, directions):
        frequency = (1- ((direction *range_rate.getRange()) / c)) * f0
        frequencies.append(frequency)
    return frequencies

def getDirections(range_rates: [StateVector], state_vectors: [StateVector]):
    directions = []

    for range_rate, state_vec in zip(range_rates, state_vectors):
        new_vec = state_vec.plus(range_rate)
        if (new_vec.minus(doptrack).getRange() < state_vec.minus(doptrack).getRange()):
            directions.append(-1)
        else:
            directions.append(1)
    return directions


def getTimes(start_time, end_time, dt):
    times = []
    current_time = start_time

    while current_time < end_time:
        times.append(current_time)
        current_time = current_time + datetime.timedelta(seconds=dt)
    return times

def plotStuff():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    PlotHelper.scatterStatevectors(ax, state_vectors, color='b', marker='D')
    PlotHelper.scatterStatevectors(ax, [doptrack])
    # PlotHelper.plotStatevectorsToPoint(ax, state_vectors, dopStateVec)
    # PlotHelper.scatterStatevectors(ax, doptrack_vectors)
    PlotHelper.scatterStatevectors(ax, ellipsoid, color='g', marker='x')
    PlotHelper.scatterStatevectors(ax, prime_meridian_vernal_equinox, color='g')
    PlotHelper.plotAxesMarkers(ax)
    # PlotHelper.plotLines(ax, state_vectors, doptrack_vectors)

dt = 1

state_vectors = getStateVectors(startRecord, endRecord, dt)
ellipsoid = getEarthPoints()

prime_meridian_vernal_equinox = getPrimeMeridian()

unit_vectors = getUnitVectors(state_vectors, doptrack)
# range_rates = getRangeRates(state_vectors, unit_vectors)
# directions = getDirections(range_rates, state_vectors)
#
# freqs = getFrequencies(range_rates, directions, 145.935e6)
range_rates = rangeRateTest(state_vectors, unit_vectors)
freqs = freqTest(range_rates, tuning_freq) #145.935e6)
tijd = getTimes(startRecord, endRecord, dt) # np.arange(len(freqs))
dates = matplotlib.dates.date2num(tijd)

fig, ax = plt.subplots()
plt.plot_date(freqs, dates, xdate=False, ydate=True)
ax.yaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M:%S'))
# plt.scatter(freqs, tijd)
# plt.gca().invert_yaxis()

# print(len(freqs))
plotStuff()
plt.show()
