import numpy as np
import yaml

yaml_file = yaml.load(open('FUNcube.yml', 'r'))

ftune = yaml_file['Sat']['State']['Tuning Frequency']
sample_rate = yaml_file['Sat']['Record']['sample_rate']
duration = yaml_file['Sat']['Predict']['Length of pass']

time_step = 0.1

L = duration * sample_rate
Lpart = np.round(L/(duration/time_step))

# NFFT = np.power(2, )

filename = 'FUNcube-1_39444_201808311030.32fc'

# Start reading the file
f = open(filename,'rb')
t = np.fromfile(f,dtype = np.float32, count = -1)
n = int(len(t)/2)
# Reconstruct the complex array
v = np.zeros([n], dtype= np.complex)
v.real = t[::2]
v.imag = -t[1::2]
f.close()
