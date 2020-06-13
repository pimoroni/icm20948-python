import sys
import mock
from .tools import MockSMBus


def test_accel_gyro():
    smbus = mock.Mock()
    smbus.SMBus = MockSMBus
    sys.modules['smbus'] = smbus

    from icm20948 import ICM20948
    icm20948 = ICM20948()
    ax, ay, az, gx, gy, gz = icm20948.read_accelerometer_gyro_data()
    assert (round(ax, 2), round(ay, 2), round(az, 2), int(gx), int(gy), int(gz)) == (0.05, 0.11, 0.16, 3, 4, 5)
    del icm20948

def test_temperature():
    smbus = mock.Mock()
    smbus.SMBus = MockSMBus
    sys.modules['smbus'] = smbus

    from icm20948 import ICM20948
    icm20948 = ICM20948()
    temp_degrees = icm20948.read_temperature()
    assert (round(temp_degrees, 2) == 24)
