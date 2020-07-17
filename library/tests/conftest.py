import sys
import mock
import pytest

from .tools import MockSMBus


@pytest.fixture(scope='function', autouse=False)
def smbus():
    """Mock smbus module."""
    sys.modules['smbus'] = mock.Mock()
    sys.modules['smbus'].SMBus = MockSMBus
    yield MockSMBus
    del sys.modules['smbus']


@pytest.fixture(scope='function', autouse=False)
def smbus_fail():
    """Mock smbus module."""
    sys.modules['smbus'] = mock.Mock()
    yield sys.modules['smbus']
    del sys.modules['smbus']
