import numpy as np
import matplotlib.pyplot as plt
import tle_to_freqs as tle2f
import datafile2waterfall as d2w
import processing_functions as procf
from tqdm import trange, tqdm
from functools import reduce

from utility import write_to_file
from yaml_reader import YamlReader

PLOT_THRESHOLD = False
PLOT_CANDIDATES = False
PLOT_GROUPS = False
PLOT_ALL_CURVES = False
PLOT_FINAL_CURVES = True
PLOT_FITTED_CURVE = True
PLOT_TCA_FCA = PLOT_FITTED_CURVE or False

PLOT_ANYTHING = PLOT_THRESHOLD or PLOT_CANDIDATES or PLOT_GROUPS or PLOT_ALL_CURVES or PLOT_FINAL_CURVES or PLOT_FITTED_CURVE

filename = 'FUNcube-1_39444_201808311030'
filename = 'files/no_noise/FUNcube-1_39444_201808311030'
# filename = 'files/noise/FUNcube-1_39444_201811180940'
yml = YamlReader(filename)

# The file is processed in steps of dt
# The dt is proportional to the vertical resolution of the spectrogram
dt = 0.5
# The nfft value defines the horizontal width of the spectrogram
# nfft <= bandwidth
nfft = np.power(2, 16)

tuning_frequency = yml.tuningfrequency()
sample_rate = yml.sample_rate()
half_sample_rate = int(sample_rate/2)
samplerate_nfft_factor = sample_rate/nfft

# Assume f0, the transmitted frequency, to be the tuning frequency
# Retrieve the frequencies and times that make up the s-curve
# Shift the s-curve to the lowest frequency in the bandwidth,
# this is necessary for the next steps of finding the satellite data
f0 = tuning_frequency
freqs, times = tle2f.tle2freqs_and_times(filename, dt, f0)
shifted_freqs = np.array(freqs) - tuning_frequency - half_sample_rate

# Apply the fft on the datafile to get the waterfall array
# Apply a thershold to the waterfall
waterfall = d2w.datafile2waterfall(filename, dt, nfft)
filteredwf = (waterfall > 1.5e-6).astype(int)

# if PLOT_THRESHOLD:
# #     ax = plt.subplot()
# #     ax.imshow(filteredwf, aspect='auto')


# Find the indices of the frequencies that remain after the threshold
# has been applied
not_zero = filteredwf.nonzero()
candidate_indeces = list(set(not_zero[1]))
candidate_indeces.sort()

# Create groups/clusters of the frequencies that remain
# To be a member of an existing group, a frequency has to differ
# less than 1000 from the frequencies in the group. Otherwise, a new group is created.
candidate_groups = []
for i in trange(len(candidate_indeces), desc='making groups'):
    index = candidate_indeces[i]

    # Create a cluster if there are none present
    if len(candidate_groups) < 1:
        candidate_groups.append([index])
    else:
        if index - candidate_indeces[i-1] < 1000:
            candidate_groups[len(candidate_groups) - 1].append(index)
        else:
            candidate_groups.append([index])

if PLOT_ANYTHING:
    ax = plt.subplot()

if PLOT_CANDIDATES:
    candi_locs = np.array(list(
        map(lambda x: int(np.average(x) * samplerate_nfft_factor - half_sample_rate), candidate_groups)))
    ax.plot(candi_locs, np.zeros(len(candi_locs)) + 450, 'bo')

# Only keep the 10 groups with the most entries.
groups = candidate_groups
if len(groups) > 10:
    groups = sorted(groups, key=lambda x: -len(x))[0:10]

#threshold = np.average(list(map(lambda x: len(x), candidate_groups))) # 500
# for candidate_group in candidate_groups:
#     if True: #len(candidate_group) > threshold:
#         groups.append(candidate_group)

if PLOT_GROUPS:
    grou_locs = np.array(list(
        map(lambda x: int(np.average(x) * samplerate_nfft_factor - half_sample_rate), groups)))

    ax.plot(grou_locs, np.zeros(len(grou_locs)) + 450, 'ro')

group_locs = np.array(list(map(lambda x: int(np.average(x)), groups)))

# Find the frequencies and times of the brightest spots for each group
# A left and right frequency is searched
lfreqs = []
rfreqs = []
ltimes = []
rtimes = []
lbright = []
rbright = []
lbright_decibel = []
rbright_decibel = []
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w', 'b', 'g']
for i in trange(len(group_locs), desc='finding brightest values for each group'):
    index = group_locs[i]
    curr_freqs = shifted_freqs + index * samplerate_nfft_factor
    left_freqs = curr_freqs - 600
    right_freqs = curr_freqs + 600
    l_fs, l_ts, l_bri, l_i, l_b_d = procf.find_brightest_pixels(left_freqs, waterfall, 400, dt, sample_rate, nfft)
    r_fs, r_ts, r_bri, r_i, r_b_d = procf.find_brightest_pixels(right_freqs, waterfall, 400, dt, sample_rate, nfft)
    lfreqs.append(l_fs)
    rfreqs.append(r_fs)
    ltimes.append(l_ts)
    rtimes.append(r_ts)
    lbright.append(l_bri)
    rbright.append(r_bri)
    lbright_decibel.append(l_b_d)
    rbright_decibel.append(r_b_d)

    if PLOT_ALL_CURVES:
        plt.plot(l_fs, l_ts, colors[i])
        plt.plot(r_fs, r_ts, colors[i])
        print(i, colors[i], l_bri + r_bri)

# Find the index of the brightest
best_index = 0
best_val = - np.inf
for i in range(len(lbright)):
    lb = lbright[i]
    rb = rbright[i]
    if (lb+rb) > best_val:
        best_val = lb+rb
        best_index = i


# Find Carier Frequency
actual_data = {
    "carrier": {
        "freqs": [],
        "times": []
    },
    "left": {
        "freqs": [],
        "power": [],
        "times": []
    },
    "right": {
        "freqs": [],
        "power": [],
        "times": []
    }
}

for lfreq, lt, lbd, rfreq, rt, rbd in zip(lfreqs[best_index], ltimes[best_index], lbright_decibel[best_index],
                                          rfreqs[best_index], rtimes[best_index], rbright_decibel[best_index]):
    if lt == rt:
        if lt not in actual_data["carrier"]["times"]:
            diff = rfreq-lfreq
            actual_data["carrier"]["freqs"].append(lfreq + (diff/2))
            actual_data["carrier"]["times"].append(lt)
            actual_data["left"]["freqs"].append(lfreq)
            actual_data["left"]["times"].append(lt)
            actual_data["left"]["power"].append(lbd)
            actual_data["right"]["freqs"].append(rfreq)
            actual_data["right"]["times"].append(rt)
            actual_data["right"]["power"].append(rbd)

poly_temp = np.polyfit(actual_data["carrier"]["freqs"], actual_data["carrier"]["times"], 3)
p = np.poly1d(poly_temp)
doublederive = p.deriv().deriv()
closest_aproach_index = np.argmin(np.abs(doublederive(actual_data["carrier"]["freqs"])))
tca = actual_data["carrier"]["times"][closest_aproach_index]
fca = actual_data["carrier"]["freqs"][closest_aproach_index]

actual_data["tca"] = tca
actual_data["fca"] = fca


write_to_file(actual_data, yml, filename)

if PLOT_FITTED_CURVE:
    ax.plot(actual_data["carrier"]["freqs"], p(actual_data["carrier"]["freqs"]), '--')

if PLOT_TCA_FCA:
    ax.plot([actual_data["carrier"]["freqs"][closest_aproach_index]], [actual_data["carrier"]["times"][closest_aproach_index]], 'mo')

if PLOT_FINAL_CURVES:
    ax.plot(actual_data["carrier"]["freqs"], actual_data["carrier"]["times"], 'go')
    ax.plot(actual_data["left"]["freqs"], actual_data["left"]["times"], 'co')
    ax.plot(actual_data["right"]["freqs"], actual_data["right"]["times"], 'mo')

if PLOT_ANYTHING:
    ax.imshow(10 * np.log10(waterfall), aspect='auto',
              extent=[-half_sample_rate, half_sample_rate, ltimes[best_index][-1], 0])
    ax.set_xlabel('Frequency offset to ' + str(tuning_frequency / 1e6) + 'MHz [Hz]')
    ax.set_ylabel('Time after start of recording [s]')

    plt.show()
