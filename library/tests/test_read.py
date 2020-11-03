def test_accel_gyro(smbus):
    from icm20948 import ICM20948
    icm20948 = ICM20948()
    ax, ay, az, gx, gy, gz = icm20948.read_accelerometer_gyro_data()
    assert (round(ax, 2), round(ay, 2), round(az, 2), int(gx), int(gy), int(gz)) == (0.05, 0.11, 0.16, 3, 4, 5)
    del icm20948


def test_magnetometer(smbus):
    from icm20948 import ICM20948
    icm20948 = ICM20948()
    x, y, z = icm20948.read_magnetometer_data()
    assert (round(x, 2), round(y, 2), round(z, 2)) == (16.65, 33.3, 49.95)
    del icm20948


def test_temperature(smbus):
    from icm20948 import ICM20948
    icm20948 = ICM20948()
    temp_degrees = icm20948.read_temperature()
    assert (round(temp_degrees, 2) == 24)
