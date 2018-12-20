import numpy as np
import yaml
from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt
from tqdm import tqdm

filename = 'FUNcube-1_39444_201808311030.32fc'
yaml_file = yaml.load(open('FUNcube.yml', 'r'))

ftune = yaml_file['Sat']['State']['Tuning Frequency']
Fs = int(yaml_file['Sat']['Record']['sample_rate'])
Time = int(yaml_file['Sat']['Predict']['Length of pass'])

Dt = 0.5 #second

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


waterval = []
for i in tqdm(range(int(Time/Dt))):
    v = np.fromfile(f, dtype= np.complex64, count= setWav)


    # waterval.append(  np.abs(np.fft.fftshift(fft(v, NFFT)))/setWav)
    def tooSmal(x):
        if x < -60:
            return 0
        else:
            return x


    datapoints = np.abs(np.fft.fftshift(fft(v, NFFT))) / setWav
    waterval.append(datapoints)
    # waterval.append( np.array([ tooSmal(xi) for xi in  10*np.log10(datapoints) ] ))
    # waterval.append(np.abs(fft(v, NFFT).imag))
    # print(abs(np.fft.fftshift(fft(v, NFFT))))
    # input[i] = abs(fft(v, NFFT))
    # n = len(v)
    #
    # Y = abs(np.fft.fftshift(fft(v, NFFT)))
    # waterval.append(Y)
f.close()
# plt.imsave('test.png', 10 * np.log10(waterval))
plt.imshow(waterval)
# water = [item for sublist in waterval for item in sublist]
# w = [item for sublist in w2 for item in sublist]
# plt.specgram(water, NFFT=NFFT, Fs=Fs)
# # for water in waterval:
# #     plt.specgram(water, Fs=Fs)
#


plt.show()