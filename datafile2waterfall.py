from tqdm import tqdm, trange
from scipy.fftpack import fft
from yaml_reader import YamlReader
import numpy as np


def datafile2waterfall(filename, dt, nfft, left_frequency=None, right_frequency=None):
    yml = YamlReader(filename)

    sample_rate = yml.sample_rate()  # amount of samples per second
    length_of_pass = yml.duration()  # in seconds

    steps = int(np.ceil(length_of_pass / dt))
    total_samples = length_of_pass * sample_rate
    samples_per_step = int(total_samples / steps)

    left_frequency_index = None
    right_frequency_index = None

    if left_frequency and right_frequency:
        left_frequency_index = frequency2array_index(left_frequency, sample_rate, nfft)
        right_frequency_index = frequency2array_index(right_frequency, sample_rate, nfft)
        waterfall = np.zeros((steps, right_frequency_index - left_frequency_index))
    else:
        waterfall = np.zeros((steps, nfft))

    filename_32fc = filename + '.32fc'
    f = open(filename_32fc, 'rb')

    for i in tqdm(range(steps), desc='Calculating Waterfall'):
        v = np.fromfile(f, dtype=np.complex64, count=samples_per_step)
        data_points = np.abs(np.fft.fftshift(fft(v, nfft))) / samples_per_step

        if left_frequency_index:
            filtered = data_points[left_frequency_index:right_frequency_index]
            waterfall[i] = filtered
        else:
            waterfall[i] = data_points
    f.close()
    return waterfall


def frequency2array_index(frequency, sample_rate, nfft) -> int:
    return int((frequency + (sample_rate/2)) / (sample_rate / nfft))
