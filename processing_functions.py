import numpy as np
from tqdm import trange


def find_brightest_pixels(freqs, waterfall, bandwidth, dt, sample_rate, nfft):
    locs = []
    ts = []
    indices = []
    total_brightness = 0
    brightness_decibel = []

    for i in range(len(waterfall)):
        next10 = waterfall[i:i+20]

        brightest_value = - np.inf
        brightest_index = 0
        brightest_time = 0
        for j in range(len(next10)):
            line = waterfall[i+j]
            freq = freqs[i+j]
            half_bandwidth = int(bandwidth / 2)
            left_index = frequency2index(freq - half_bandwidth, sample_rate, nfft)
            right_index = frequency2index(freq + half_bandwidth, sample_rate, nfft)
            part_of_array = line[left_index: right_index]

            if len(part_of_array) > 0:
                brightest_candidate_index = np.argmax(part_of_array)
                brightest_candidate_value = part_of_array[brightest_candidate_index]
                if brightest_candidate_value > brightest_value:
                    brightest_value = brightest_candidate_value
                    brightest_index = brightest_candidate_index + left_index
                    brightest_time = i+j
        total_brightness += brightest_value
        brightness_decibel.append(10 * np.log10(brightest_value))
        locs.append(index2frequency(brightest_index, sample_rate, nfft))
        ts.append(brightest_time*dt)
        indices.append(brightest_index)
    return locs, ts, total_brightness, indices, brightness_decibel


def frequency2index(freq, sample_rate, nfft):
    return int(np.max([0, (freq + int(sample_rate/2)) / (sample_rate/nfft)]))


def index2frequency(index, sample_rate, nfft):
    return int((index * (sample_rate/nfft)) - int(sample_rate/2))
