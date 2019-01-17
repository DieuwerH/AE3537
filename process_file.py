import numpy as np
import matplotlib.pyplot as plt
import tle_to_freqs as tle2f
import datafile2waterfall as d2w
import processing_functions as procf
from tqdm import trange, tqdm

from yaml_reader import YamlReader

filename = 'FUNcube-1_39444_201808311030'
yml = YamlReader(filename)

dt = 0.5
nfft = np.power(2, 16)

tuning_frequency = yml.tuningfrequency()
sample_rate = yml.sample_rate()
half_sample_rate = int(sample_rate/2)
samplerate_nfft_factor = sample_rate/nfft

f0 = tuning_frequency
freqs, times = tle2f.tle2freqs_and_times(filename, dt, f0)
shifted_freqs = np.array(freqs) - tuning_frequency - half_sample_rate

waterfall = d2w.datafile2waterfall(filename, dt, nfft)
filteredwf = (waterfall > 1.5e-6).astype(int)

not_zero = filteredwf.nonzero()
candidate_indeces = list(set(not_zero[1]))
candidate_indeces.sort()

candidate_groups = []
for i in trange(len(candidate_indeces), desc='making groups'):
    index = candidate_indeces[i]
    if len(candidate_groups) < 1:
        candidate_groups.append([index])
    else:
        if index - candidate_indeces[i-1] < 1000:
            candidate_groups[len(candidate_groups) - 1].append(index)
        else:
            candidate_groups.append([index])

groups = []
for candidate_group in candidate_groups:
    if len(candidate_group) > 500:
        groups.append(candidate_group)

group_locs = np.array(list(map(lambda x: int(np.average(x)), groups)))

lfreqs = []
rfreqs = []
ltimes = []
rtimes = []
lbright = []
rbright = []
for i in trange(len(group_locs), desc='finding brightest values for each group'):
    index = group_locs[i]
    curr_freqs = shifted_freqs + index * samplerate_nfft_factor
    left_freqs = curr_freqs - 600
    right_freqs = curr_freqs + 600
    l_fs, l_ts, l_bri, l_i = procf.find_brightest_pixels(left_freqs, waterfall, 400, dt, sample_rate, nfft)
    r_fs, r_ts, r_bri, r_i = procf.find_brightest_pixels(right_freqs, waterfall, 400, dt, sample_rate, nfft)
    lfreqs.append(l_fs)
    rfreqs.append(r_fs)
    ltimes.append(l_ts)
    rtimes.append(r_ts)
    lbright.append(l_bri)
    rbright.append(r_bri)

# fig, ax = plt.subplots(ncols=len(lfreqs))
# for i in range(len(lfreqs)):
#     plt.plot(lfreqs[i], ltimes[i])
#     plt.plot(rfreqs[i], rtimes[i])
# plt.imshow(10 * np.log10(waterfall), aspect='auto', extent=[-half_sample_rate, half_sample_rate, ltimes[0][-1], 0])

best_index = 0
best_val = - np.inf
for i in range(len(lbright)):
    lb = lbright[i]
    rb = rbright[i]
    if (lb+rb) > best_val:
        best_val = lb+rb
        best_index = i


# Find Carier Frequency
carrier_fs = []
carrier_ts = []
for lfreq, lt, rfreq, rt in zip(lfreqs[best_index], ltimes[best_index], rfreqs[best_index], rtimes[best_index]):
    if lt == rt:
        diff = rfreq-lfreq
        carrier_fs.append(lfreq + (diff/2))
        carrier_ts.append(lt)

ax = plt.subplot()

ax.plot(lfreqs[best_index], ltimes[best_index])
ax.plot(rfreqs[best_index], rtimes[best_index])
ax.plot(carrier_fs, carrier_ts)
ax.imshow(10 * np.log10(waterfall), aspect='auto', extent=[-half_sample_rate, half_sample_rate, ltimes[best_index][-1], 0])
ax.set_xlabel('Frequency offset to ' + str(tuning_frequency / 1e6) + 'MHz [Hz]')
ax.set_ylabel('Time after start of recording [s]')