import datafile2waterfall
from SteetVector import StateVector
import yaml
import yaml_reader
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
import datetime
import numpy as np
import matplotlib.pyplot as plt

from tle_to_freqs import tle2freqs


def _get_loaded_yaml(filename):
    opened = open(filename, 'r')
    return yaml.load(opened)


def _get_statevectors(loaded_yaml, dt):
    start_record = yaml_reader.extractStartRecordTime(loaded_yaml)
    end_record = yaml_reader.extractEndRecordTime(loaded_yaml)
    satellite = _get_satellite(loaded_yaml)

    state_vectors = []
    current_time = start_record

    while current_time < end_record:
        pos, vel = satellite.propagate(current_time.year, current_time.month, current_time.day,
                                       current_time.hour, current_time.minute, current_time.second)
        state_vector = StateVector(np.array(pos)*1000, np.array(vel)*1000, current_time)
        state_vector.calculate_ecef()
        state_vectors.append(state_vector)

        current_time = current_time + datetime.timedelta(seconds=dt)
    return state_vectors


def _get_satellite(loaded_yaml):
    line1, line2 = yaml_reader.extraceLines(loaded_yaml)
    return twoline2rv(line1, line2, wgs72)


filename = "FUNcube-1_39444_201808311030"

waterfall = datafile2waterfall.datafile2waterfall(filename, 0.5, np.power(2, 16))
frequencies = tle2freqs(filename, 0.5)
plt.imshow(10*np.log10(waterfall))
plt.show()