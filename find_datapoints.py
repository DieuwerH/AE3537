import datafile2waterfall
import tle_to_freqs
import numpy as np
import matplotlib.pyplot as plt
from yaml_reader import YamlReader
from skimage import filters

filename = 'FUNcube-1_39444_201808311030'
yml = YamlReader(filename)
dt = 0.5
nfft = np.power(2, 16)
f0 = 146005152  # actual value
# f0 = 145.92e6  # transmitted frequency
ftune = yml.tuningfrequency()
half_sample_rate = int(yml.sample_rate()/2)
# f0 = ftune
# f0 = ftune - half_sample_rate
# f0 = ftune + half_sample_rate

signal_width = 1200
left_frequency = 3e4
right_frequency = 4e4
waterfall = datafile2waterfall.datafile2waterfall(filename, dt, nfft, left_frequency, right_frequency)
frequencies, times = tle_to_freqs.tle2freqs_and_times(filename, dt, f0)


def shift_frequencies(freqs, left_freq):
    lowest_freq = np.min(freqs)
    diff = lowest_freq - left_freq
    return np.array(freqs)-diff + (signal_width/2)

corrected_freqs = np.array(frequencies) - ftune
# corrected_freqs = shift_frequencies(frequencies, left_frequency)
left_line = corrected_freqs - 600
right_line = corrected_freqs + 600


def find_brightest_pixels(freqs, wfall, bandwidth):
    locs = []

    for i in range(len(wfall)):
        waterfall_line = wfall[i]
        frequency = freqs[i]
        half_bandwidth = int(bandwidth / 2)
        left_index = frequency2index(frequency - half_bandwidth, left_frequency, right_frequency, len(waterfall_line))
        right_index = frequency2index(frequency + half_bandwidth, left_frequency, right_frequency, len(waterfall_line))
        part_of_array = waterfall_line[left_index: right_index]
        highest = np.argmax(part_of_array) + left_index
        locs.append(index2frequency(highest, left_frequency, right_frequency, len(waterfall_line)))
    return locs


def find_brightest_pixels2(freqs, wfall, bandwidth):
    locs = []
    ts = []
    brightness = 0

    for i in range(len(wfall)):
        next10 = wfall[i:i+20]

        brightest_value = - np.inf
        brightest_index = 0
        brightest_time = 0
        for j in range(len(next10)):
            line = wfall[i+j]
            freq = freqs[i+j]
            half_bandwidth = int(bandwidth / 2)
            left_index = frequency2index(freq - half_bandwidth, left_frequency, right_frequency,
                                         len(line))
            right_index = frequency2index(freq + half_bandwidth, left_frequency, right_frequency,
                                          len(line))
            part_of_array = line[left_index: right_index]
            brightest_candidate_index = np.argmax(part_of_array)
            brightest_candidate_value = part_of_array[brightest_candidate_index]
            if brightest_candidate_value > brightest_value:
                brightest_value = brightest_candidate_value
                brightest_index = brightest_candidate_index + left_index
                brightest_time = i+j
        brightness += brightest_value
        locs.append(index2frequency(brightest_index, left_frequency, right_frequency, len(wfall[0])))
        ts.append(brightest_time*dt)
    return locs, ts, brightness


def frequency2index(freq, lfreq, rfreq, width):
    return int(np.max([0,(freq - lfreq) / ((rfreq - lfreq) / width)]))


def index2frequency(index, lfreq, rfreq, width):
    return int((index * ((rfreq-lfreq)/width)) + lfreq)


def find_carrier_frequency(lfreqs, lts, rfreqs, rts):
    fs = []
    ts = []
    for lfreq, lt, rfreq, rt in zip(lfreqs, lts, rfreqs, rts):
        if lt == rt:
            diff = rfreq-lfreq
            fs.append(lfreq + (diff/2))
            ts.append(lt)
    return fs, ts


def plot_figures():
    fig, ax = plt.subplots(ncols=2)
    ax[0].plot(corrected_freqs, times, 'b')
    ax[0].plot(left_line, times, 'c')
    ax[0].plot(right_line, times, 'm')
    ax[0].imshow(10 * np.log10(waterfall), aspect='auto', extent=[left_frequency, right_frequency, times[-1], 0])

    ax[1].plot(corrected_freqs, times, 'b')
    ax[1].plot(left_line, times, 'c')
    ax[1].plot(right_line, times, 'm')
    ax[1].imshow(10 * np.log10(edges), aspect='auto', extent=[left_frequency, right_frequency, times[-1], 0])

    fig, ax3 = plt.subplots(ncols=2)
    ax3[0].plot(left_locs[100:-200], ts_l[100:-200], 'bo')
    ax3[0].plot(right_locs[100:-200], ts_r[100:-200], 'ro')
    ax3[0].plot(carrier_f, carrier_t, 'mo')
    ax3[0].plot(x_new, y_new)
    ax3[0].imshow(10 * np.log10(waterfall), aspect='auto', extent=[left_frequency, right_frequency, times[-1], 0])
    ax3[0].plot(left_line, times, 'c')

    ax3[1].plot(left_locs2, ts_l2, 'bo')
    ax3[1].plot(right_locs_2, ts_r2, 'ro')
    ax3[1].imshow(10 * np.log10(edges), aspect='auto', extent=[left_frequency, right_frequency, times[-1], 0])
    ax3[1].plot(left_line, times, 'c')


edges = filters.sobel(waterfall)
left_locs, ts_l, brigl = find_brightest_pixels2(left_line, waterfall, 400)
right_locs, ts_r, brigr = find_brightest_pixels2(right_line, waterfall, 400)
left_locs2, ts_l2, brigl2 = find_brightest_pixels2(left_line, edges, 400)
right_locs_2, ts_r2, brigr2 = find_brightest_pixels2(right_line, edges, 400)

carrier_f, carrier_t = find_carrier_frequency(left_locs, ts_l, right_locs, ts_r)

z = np.polyfit(carrier_f, carrier_t, 7)
f = np.poly1d(z)

x_new = np.linspace(carrier_f[0], carrier_f[-1])
y_new = f(x_new)


plot_figures()

plt.show()
