#!/usr/bin/env python

from icm20948 import ICM20948
import time
import math

print("""magnetometer.py - Convert raw values to heading

Rotate the sensor (X-axis upwards) through 360 degrees to calibrate.

Press Ctrl+C to exit!

""")

X = 0
Y = 1
Z = 2

AXES = Y, Z

imu = ICM20948()

amin = list(imu.read_magnetometer_data())
amax = list(imu.read_magnetometer_data())

while True:
    mag = list(imu.read_magnetometer_data())
    for i in range(3):
        v = mag[i]
        if v < amin[i]:
            amin[i] = v
        if v > amax[i]:
            amax[i] = v
        mag[i] -= amin[i]
        try:
            mag[i] /= amax[i] - amin[i]
        except ZeroDivisionError:
            pass
        mag[i] -= 0.5

    heading = math.atan2(
            mag[AXES[0]],
            mag[AXES[1]])

    if heading < 0:
        heading += 2 * math.pi
    heading = math.degrees(heading)
    heading = round(heading)

    print("Heading: {}".format(heading))

    time.sleep(0.1)
