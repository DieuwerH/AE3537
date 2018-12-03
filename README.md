# AE3537
Spaceflight assignment 2018

In this assignment I will transform TLE data to a Doppler shifted S-curve.

This S-curve will help me to extract datapoints from raw radio data received at the Doptrack station in Delft.

## Approach
1. Use sgp4 propagator to retrieve positions of satellite during time of recording.
2. Rotate these points based on datetime, so you go from earth centered inertial to earth centered earth fixed reference frame
3. Convert LatLonHeight of Doptrack to Cartesian coordinates
4. Also rotate doptrack coordinates based on time
5. Find unit vectors pointing from the satellite to Doptrack
6. Scale these vectors based on the velocity of the satellite to retrieve the rangerate

## TODO
1. Find f0 (broadcasted frequency)
2. With f0, convert range rates to frequencies received at the doptrack station using the doppler formula
3. Convert the received frequencies to power intesity
4. Create s-curve using this data
5. Fit generated s-curve to actual received s-curve
6. Extract data points from actual s-curve with the help of generated s-curve 