import datetime
import pytz
import tle_functions
import PlotHelper
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
tuning_freq = yaml_reader.extractTuningFrequency(loaded)

vernalEquinox = datetime.datetime(2018, 3, 20, 16, 15, 0, 0, pytz.UTC)
ut1 = 86164.090530

doptrack = LatLon(51.99888889, 4.37333333, height=134.64, name='DopTrackStation').toCartesian()
# From http://www.apsalin.com/convert-geodetic-to-cartesian.aspx :
centerEarth = StateVector(0, 0, 0, 0, 0, 0)
dopStateVec = StateVector(3923683.03350176, 300074.043717263, 5002833.32624071, 0, 0, 0)
satellite = twoline2rv(line1, line2, wgs72)
#
# c = 299792 # km/s , value from google
c = 299792458 #m/s

def getStateVectors(starttime, endtime, delta_seconds):
    state_vecs = []
    current_time = starttime

    while current_time < endtime:
        pos, vel = satellite.propagate(current_time.year, current_time.month, current_time.day, current_time.hour,
                                       current_time.minute, current_time.second)
        state_vec = StateVector(pos[0]*1000, pos[1]*1000, pos[2]*1000,
                                vel[0]*1000, vel[1]*1000, vel[2]*1000)
        state_vec.rotate_time(current_time)
        state_vecs.append(state_vec)

        current_time = current_time + datetime.timedelta(0, delta_seconds)
    return state_vecs


def getDoptrackVec(starttime, endtime, delta_seconds):
    doptrack_vectors = []
    current_time = starttime

    while current_time < endtime:
        doptrack_vec = StateVector(doptrack.x / 1000, doptrack.y / 1000, doptrack.z / 1000, 0, 0, 0)
        doptrack_vec.rotate_time(current_time)
        doptrack_vectors.append(doptrack_vec)

        current_time = current_time + datetime.timedelta(0, delta_seconds)
    return doptrack_vectors


def getRotatedDopVecs(start_time, end_time, delta_seconds):
    doptrack_vectors = []
    current_time = start_time

    while current_time < end_time:
        dop_vec = copy.copy(dopStateVec)
        dop_vec.rotate_time(current_time)
        doptrack_vectors.append(dop_vec)

        current_time = current_time + datetime.timedelta(0, delta_seconds)
    return doptrack_vectors


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
        if (new_vec.minus(dopStateVec).getRange() < state_vec.minus(dopStateVec).getRange()):
            directions.append(-1)
        else:
            directions.append(1)
    return directions

def plotStuff():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    PlotHelper.scatterStatevectors(ax, state_vectors, color='b', marker='D')
    PlotHelper.scatterStatevectors(ax, [dopStateVec])
    # PlotHelper.plotStatevectorsToPoint(ax, state_vectors, dopStateVec)
    # PlotHelper.scatterStatevectors(ax, doptrack_vectors)
    PlotHelper.scatterStatevectors(ax, ellipsoid, color='g', marker='x')
    PlotHelper.scatterStatevectors(ax, prime_meridian_vernal_equinox, color='g')
    PlotHelper.plotAxesMarkers(ax)
    # PlotHelper.plotLines(ax, state_vectors, doptrack_vectors)

    plt.show()

dt = 1

state_vectors = getStateVectors(startRecord, endRecord, dt)
# doptrack_vectors = getRotatedDopVecs(startRecord, endRecord, 10)  # getDoptrackVec(startRecord, endRecord, 10)

ellipsoid = getEarthPoints()

prime_meridian_vernal_equinox = getPrimeMeridian()

unit_vectors = getUnitVectors(state_vectors, dopStateVec)
# range_rates = getRangeRates(state_vectors, unit_vectors)
# directions = getDirections(range_rates, state_vectors)
#
# freqs = getFrequencies(range_rates, directions, 145.935e6)
range_rates = rangeRateTest(state_vectors, unit_vectors)
freqs = freqTest(range_rates, 145.935e6)
tijd = np.arange(len(freqs))
plt.scatter(freqs, tijd)
# plt.gca().invert_yaxis()
plt.show()
# print(len(freqs))

plotStuff()
