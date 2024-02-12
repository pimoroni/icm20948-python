#!/usr/bin/env python

import time

from icm20948 import ICM20948

print("""read-all.py

Reads all ranges of movement: accelerometer, gyroscope and

compass heading.

Press Ctrl+C to exit!

""")

imu = ICM20948()

while True:
    x, y, z = imu.read_magnetometer_data()
    ax, ay, az, gx, gy, gz = imu.read_accelerometer_gyro_data()

    print("""
Accel: {:05.2f} {:05.2f} {:05.2f}
Gyro:  {:05.2f} {:05.2f} {:05.2f}
Mag:   {:05.2f} {:05.2f} {:05.2f}""".format(
        ax, ay, az, gx, gy, gz, x, y, z
        ))

    time.sleep(0.25)
