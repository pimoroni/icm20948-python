#!/usr/bin/env python

from icm20948 import ICM20948
from rgbmatrix5x5 import RGBMatrix5x5
from colorsys import hsv_to_rgb
import time
import math

print("""magnetometer-to-rgb5x5.py - Convert heading to colour

Converts the raw heading to a colour by treating it as hue.

Requires a 5x5 RGB Matrix breakout.

Rotate the sensor (X-axis upwards) through 360 degrees to calibrate.

Press Ctrl+C to exit!

""")

X = 0
Y = 1
Z = 2

AXES = Y, Z

imu = ICM20948()
rgbmatrix5x5 = RGBMatrix5x5()
rgbmatrix5x5.set_clear_on_exit()
rgbmatrix5x5.set_brightness(0.8)


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
    heading = int(round(heading))


    r, g, b = [int(c * 255.0) for c in hsv_to_rgb(heading / 360.0, 1.0, 1.0)]

    print("Heading: {:3d} Color: #{:02X}{:02X}{:02X}".format(heading, r, g, b))

    rgbmatrix5x5.set_all(r, g, b)
    rgbmatrix5x5.show()

    time.sleep(0.1)
