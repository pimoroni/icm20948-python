import sys

import mock
import pytest

from .tools import MockSMBus


@pytest.fixture(scope='function', autouse=False)
def smbus():
    """Mock smbus module."""
    sys.modules['smbus2'] = mock.Mock()
    sys.modules['smbus2'].SMBus = MockSMBus
    yield MockSMBus
    del sys.modules['smbus2']


@pytest.fixture(scope='function', autouse=False)
def smbus_fail():
    """Mock smbus module."""
    sys.modules['smbus2'] = mock.Mock()
    yield sys.modules['smbus2']
    del sys.modules['smbus2']
