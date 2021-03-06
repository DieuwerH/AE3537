#!/usr/bin/python

import sys, getopt
import numpy as np
from scipy.fftpack import fft, ifft
import matplotlib as mpl
import matplotlib.cm as cmMat
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.io as sio
import yaml


# input arguments handling

def main(argv):
    inputfile = ''
    outputfile = ''
    metafile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:m:", ["ifile=", "ofile=", "mfile="])
    except getopt.GetoptError:
        print
        'spectrogram.py -i <inputfile> -o <outputfile> -m <metafile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print
            'spectogram.py -i <inputfile> -o <outputfile> -m <metafile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-m", "--mfile"):
            metafile = arg
    # print 'Input file is "', inputfile
    # print 'Output file is "', outputfile

    # read in metafile
    with open(metafile, 'r') as metaf:
        meta = yaml.load(metaf)
    metaf.close()

    # input filename
    inputfilename = inputfile

    # initail values
    Time = int(meta['Sat']['Predict']['Length of pass'])
    Fs = int(meta['Sat']['Record']['sample_rate'])
    Dt = 0.5;

    # Construct other information
    L = Time * Fs
    setWav = int(2 * L / (Time / Dt))

    # get optimal NFFT value
    # n2 = 1 #nextpow 2 algoritm
    # while n2 < L/Time/Dt: n2 *= 2
    # NFFT = 2.^n2
    NFFT = 65536
    # half = NFFT/2

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

    Waterfall = np.zeros([int(Time / Dt), numC], dtype='float')

    # Initialize Matrices
    forend = int(Time / Dt)
    f = open(inputfilename, 'rb')
    for i in range(0, forend):
        # start reading the file
        t = np.fromfile(f, dtype=np.float32, count=setWav)
        n = len(t) / 2

        # Reconstruct the complex array
        v = np.zeros([int(n)], dtype=np.complex)
        v.real = t[::2]
        v.imag = -t[1::2]

        # generate the fft of the signal
        Y = fft(v, NFFT)
        dum = 2 * abs(Y[0:NFFT + 1] / setWav)
        half = len(dum) / 2

        # fill in the Waterfall matrix
        line = np.zeros(dum.shape)
        line[0:int(half)] = dum[int(half):]
        line[int(half):] = dum[0:int(half)]
        line = line.conj().transpose()
        # line = line[::-1]

        invec = line[lfreq:rfreq + 1]
        Waterfall[i, :] = 10 * np.log10(invec)
        print(i + 1)
        sys.stdout.write("\033[F")

    f.close()
    print(i + 1)

    # create colorbar: now not used
    plt.imsave(outputfile, Waterfall, cmap=cmMat.gray)


if __name__ == "__main__":
    main(sys.argv[1:])
