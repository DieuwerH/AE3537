from pygeodesy.ellipsoidalKarney import Cartesian
from pygeodesy.ellipsoidalKarney import LatLon
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

satellite = Cartesian(3145.5036885,  5387.14337206, 3208.93193301)
satellite = satellite.toLatLon()
doptrack = LatLon(51.99888889,4.37333333)
doptrack = LatLon(51.99888889, 4.37333333, height=134.64, name='DopTrackStation')
print(doptrack.distanceTo(satellite))

ellipsoid = []

for lat in range(18):
    for lon in range (36):
        point = LatLon((lat*10) - 90, (lon*10) - 180)
        ellipsoid.append(point.toCartesian())

xs = list(map(lambda x: x.x, ellipsoid))
ys = list(map(lambda x: x.y, ellipsoid))
zs = list(map(lambda x: x.z, ellipsoid))

xs = np.asarray(xs)
ys = np.asarray(ys)
zs = np.asarray(zs)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(xs, ys, zs, c='r')
# ax.scatter(xs, ys, zs)
# Axes3D.plot_wireframe(ax, X=xs, Y=ys, Z=zs)


plt.show()