import sys
import mock
import pytest
from .tools import MockSMBus


def test_setup():
    sys.modules['smbus'] = mock.Mock()

    from icm20948 import ICM20948

    with pytest.raises(RuntimeError):
        icm20948 = ICM20948()
        del icm20948


def test_setup_present():
    smbus = mock.Mock()
    smbus.SMBus = MockSMBus
    sys.modules['smbus'] = smbus

    from icm20948 import ICM20948
    icm20948 = ICM20948()
    del icm20948
