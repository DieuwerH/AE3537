import datetime
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

vernalEquinox = datetime.datetime(2018, 3, 20, 17, 15, 0, 0)
ut1 = 86164.090530

doptrack = LatLon(51.99888889, 4.37333333, height=134.64, name='DopTrackStation').toCartesian()
# From http://www.apsalin.com/convert-geodetic-to-cartesian.aspx :
centerEarth = StateVector(0, 0, 0, 0, 0, 0)
dopStateVec = StateVector(3923683.03350176 / 1000, 300074.043717263 / 1000, 5002833.32624071 / 1000, 0, 0, 0)
satellite = twoline2rv(line1, line2, wgs72)

c = 299792 # km/s , value from google


def getStateVectors(starttime, endtime, delta_seconds):
    state_vecs = []
    current_time = starttime

    while current_time < endtime:
        pos, vel = satellite.propagate(current_time.year, current_time.month, current_time.day, current_time.hour,
                                       current_time.minute, current_time.second)
        state_vec = StateVector(pos[0], pos[1], pos[2], vel[0], vel[1], vel[2])
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
            point = StateVector(point.x / 1000, point.y / 1000, point.z / 1000, 0, 0, 0)
            ellipsoid.append(point)
    return ellipsoid


def getPrimeMeridian():
    prime_meridian_vernal_equinox = []
    prime_meridian_at_start = []
    for lat in range(18):
        point_cartesian = LatLon((lat * 10) - 90, 0).toCartesian()
        point = StateVector(point_cartesian.x / 1000, point_cartesian.y / 1000, point_cartesian.z / 1000, 0, 0, 0)
        prime_meridian_vernal_equinox.append(point)
        point_ = StateVector(point_cartesian.x / 1000, point_cartesian.y / 1000, point_cartesian.z / 1000, 0, 0, 0)
        point_.rotate_time(startRecord)
        prime_meridian_at_start.append(point_)
    return prime_meridian_vernal_equinox, prime_meridian_at_start


def getUnitVectors(sat_vecs, dop_vecs):
    unit_vectors = []
    for sat, dop in zip(sat_vecs, dop_vecs):
        sat_to_dop = dop.minus(sat)
        length = sat_to_dop.getRange()
        unit_s_t_d = sat_to_dop.divide(length)
        unit_vectors.append(unit_s_t_d)
    return unit_vectors


def getRangeRates(state_vectors, unit_vectors):
    range_rates = []

    for cur_unit, cur_vel in zip(unit_vectors, state_vectors):
        range_rate = cur_unit.times(cur_unit.dotPosVel(cur_vel))
        range_rates.append(range_rate)

    return range_rates

def getFrequencies(range_rates, f0):
    frequencies = []

    for range_rate in range_rates:
        frequency = (1-range_rate / c) * f0
        frequencies.append(frequency)
    return frequencies

state_vectors = getStateVectors(startRecord, endRecord, 10)
doptrack_vectors = getRotatedDopVecs(startRecord, endRecord, 10)  # getDoptrackVec(startRecord, endRecord, 10)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

PlotHelper.scatterStatevectors(ax, state_vectors, color='b', marker='D')
PlotHelper.scatterStatevectors(ax, doptrack_vectors)

ellipsoid = getEarthPoints()
PlotHelper.scatterStatevectors(ax, ellipsoid, color='g', marker='x')

prime_meridian_vernal_equinox, prime_meridian_at_start = getPrimeMeridian()

PlotHelper.scatterStatevectors(ax, prime_meridian_vernal_equinox, color='g')
PlotHelper.scatterStatevectors(ax, prime_meridian_at_start, color='y')

PlotHelper.plotAxesMarkers(ax)

unit_vectors = getUnitVectors(state_vectors, doptrack_vectors)
range_rates = getRangeRates(state_vectors, unit_vectors)

PlotHelper.plotLines(ax, state_vectors, doptrack_vectors)

plt.show()
