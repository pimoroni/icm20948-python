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

    print(f"""
Accel: {ax:05.2f} {ay:05.2f} {az:05.2f}
Gyro:  {gx:05.2f} {gy:05.2f} {gz:05.2f}
Mag:   {x:05.2f} {y:05.2f} {z:05.2f}""")

    time.sleep(0.25)
