import pytest


def test_setup(smbus_fail):
    from icm20948 import ICM20948

    with pytest.raises(RuntimeError):
        icm20948 = ICM20948()
        del icm20948


def test_setup_present(smbus):
    from icm20948 import ICM20948
    icm20948 = ICM20948()
    del icm20948
