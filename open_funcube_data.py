import numpy as np
import yaml
from scipy.fftpack import fft
import matplotlib.pyplot as plt
from skimage import filters
from tqdm import tqdm
from tle_to_freqs import tle2freqs_and_times

SHOWIMAGE = True
SHOWFILTER = True
SAVEIMAGE = False

filename = 'FUNcube-1_39444_201808311030.32fc'
yaml_file = yaml.load(open('FUNcube-1_39444_201808311030.yml', 'r'))

ftune = yaml_file['Sat']['State']['Tuning Frequency']
Fs = int(yaml_file['Sat']['Record']['sample_rate'])
Time = int(yaml_file['Sat']['Predict']['Length of pass'])

Dt = 0.5 # seconda

# Construct other information
L = Time * Fs
setWav = int(L / (Time / Dt))
NFFT = np.power(2, 16)  #8192 #65536

# get values for axis waterfall plot
f0 = 0
nx = Fs / NFFT
ny = Dt
bandwidth = np.arange(f0 - Fs / 2 + nx / 2, Fs / 2 - nx / 2 + 1, nx)
time = np.arange(1, Time + 1, ny)

# set certain zoom area
lbound = 12000
rbound = 24000

LF = np.array((bandwidth > lbound).nonzero())
lfreq = LF.min() + 1
RF = np.array((bandwidth > rbound).nonzero())
rfreq = RF.min() + 1

tmp = bandwidth[lfreq:rfreq + 1]
numC = tmp.size


input = np.zeros(setWav, dtype=complex)
# Initialize Matrices
forend = int(Time / Dt)
# Start reading the file
f = open(filename,'rb')
# t = np.fromfile(f,dtype = np.float32, count = -1)
# n = int(len(t)/2)
# # Reconstruct the complex array
# v = np.zeros([n], dtype= np.complex)
# v.real = t[::2]
# v.imag = -t[1::2]
lfreq = 3e4
rfreq = 4e4
left_frequency_index = int((lfreq + 12.5e4) / (Fs/NFFT))
right_frequency_index = int((rfreq + 12.5e4) / (Fs/NFFT))

# waterval = []
waterval = np.zeros((int(Time/Dt), right_frequency_index-left_frequency_index))
for i in tqdm(range(int(Time/Dt))):
    v = np.fromfile(f, dtype= np.complex64, count= setWav)
    datapoints = np.abs(np.fft.fftshift(fft(v, NFFT))) / setWav

    filtered = datapoints[left_frequency_index:right_frequency_index]
    # waterval.append(datapoints)
    # waterval.append(filtered)
    waterval[i] = filtered
f.close()

lowest = np.min(waterval)
highest = np.max(waterval)
x_percent = 0.9
threshold = highest - (abs(highest - lowest) * x_percent)
filtered_waterval = (waterval >= threshold).astype(int)


def showPlots():
    fig, ax = plt.subplots(nrows=2, ncols=2)
    frequencies, times = tle2freqs_and_times('FUNcube-1_39444_201808311030.yml', 0.5)
    moved_frequencies = np.array(frequencies) - ftune + 35000
    # ax.imshow(filtered_waterval, aspect='auto')
    # print('Plotting image')
    ax[0, 0].plot(moved_frequencies, times)
    ax[0, 0].invert_yaxis()
    ax[0, 0].imshow(10 * np.log10(waterval), aspect='auto', extent=[lfreq, rfreq, Time, 0])
    ax[0, 0].set_xlabel('Frequency offset to ' + str(ftune / 1e6) + 'MHz [Hz]')
    ax[0, 0].set_ylabel('Time after start of recording [s]')

    edges = filters.sobel(waterval)
    ax[0, 1].imshow(10*np.log10(edges), aspect='auto', cmap='magma')
    ax[0, 1].set_xlabel('Frequency offset to ' + str(ftune / 1e6) + 'MHz [Hz]')
    ax[0, 1].set_ylabel('Time after start of recording [s]')

    low = 6.9e-07
    lowt = (edges > low).astype(int)
    ax[1, 0].imshow(lowt, cmap='magma')
    ax[1, 0].set_title('Low threshold')

    ax[1, 1].plot(frequencies, times)
    ax[1, 1].invert_yaxis()
    # ax[1, 1].gca().invert_yaxis()
    # plt.gca().invert_yaxis()

if SAVEIMAGE:
    print('Saving image')
    plt.imsave('test.png', 10 * np.log10(waterval))

if SHOWIMAGE:
    showPlots()


plt.show()
