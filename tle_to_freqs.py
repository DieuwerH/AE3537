import yaml
from tqdm import tqdm
from yaml_reader import YamlReader
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from SteetVector import StateVector
import datetime
import numpy as np

doptrack_station = StateVector(pos=np.array([3923683.03350176, 300074.043717263, 5002833.32624071]))
c = 299792458


def tle2freqs(filename, dt, f0=None):
    yml = YamlReader(filename)
    state_vectors = get_statevectors(yml, dt)
    if not f0:
        f0 = yml.tuningfrequency()
    rangerates = get_rangerates(state_vectors)
    return get_frequencies(rangerates, f0)


def tle2freqs_and_times(filename, dt, f0=None):
    yml = YamlReader(filename)
    return tle2freqs(filename, dt, f0), get_times(yml, dt)


def get_loaded_yaml(filename):
    opened = open(filename, 'r')
    return yaml.load(opened)


def get_satellite(yml: YamlReader):
    line1, line2 = yml.lines()
    return twoline2rv(line1, line2, wgs72)


def get_statevectors(yml: YamlReader, dt: float):
    start_record = yml.start_record_time()
    end_record = yml.end_record_time()
    satellite = get_satellite(yml)

    state_vectors = []
    current_time = start_record

    total_amount = len(get_times(yml, dt))
    progress = tqdm(total=total_amount, desc='Propagating Satellite')
    while current_time < end_record:
        pos, vel = satellite.propagate(current_time.year, current_time.month, current_time.day,
                                       current_time.hour, current_time.minute, current_time.second)
        state_vector = StateVector(np.array(pos)*1000, np.array(vel)*1000, current_time)
        state_vectors.append(state_vector)
        current_time = current_time + datetime.timedelta(seconds=dt)
        progress.update(1)
    progress.close()
    return state_vectors


def get_unitvectors(state_vectors):
    unit_vectors = []
    for satellite in tqdm(state_vectors, desc='Calculating unit vectors'):
        station2sat = satellite.pos_ecef - doptrack_station.pos_eci
        length = np.linalg.norm(station2sat)
        unit = station2sat / length
        unit_vectors.append(unit)
    return unit_vectors


def get_rangerates(state_vectors):
    unit_vectors = get_unitvectors(state_vectors)
    range_rates = []
    for unit, state_vector in tqdm(zip(unit_vectors, state_vectors), desc='Calculating rangerates'):
        range_rates.append(np.vdot(unit, state_vector.vel_ecef))
    return range_rates


def get_frequencies(range_rates, f0):
    frequencies = []
    # for range_rate in tqdm(range_rates, desc='Calculating frequencies'):
    for range_rate in range_rates:
        f = (1 + (range_rate/c))*f0
        frequencies.append(f)
    return frequencies


def get_times(yml: YamlReader, dt: float):
    start_record = yml.start_record_time()
    end_record = yml.end_record_time()
    difference = end_record - start_record
    seconds = difference.seconds + difference.microseconds/1e6
    return np.arange(0, seconds, dt)
