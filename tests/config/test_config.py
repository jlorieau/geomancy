"""Test the config module"""
from geomancy.config.config import Config, Parameter


def test_config_getset():
    """Test the Config get and set methods"""

    config = Config(value1='value1', value2=3)  # new instance--bad!

    class A:
        attribute1 = Parameter('value1')
        attribute2 = Parameter('value2')
    a = A()

    # Try measuring the values directly
    assert config.value1 == 'value1'
    assert config.value2 == 3
    assert a.attribute1 == 'value1'
    assert a.attribute2 == 3

    # Try modifying the values
    config.value1 = 'new value1'
    config.value2 = 4

    assert config.value1 == 'new value1'
    assert config.value2 == 4
    assert a.attribute1 == 'new value1'
    assert a.attribute2 == 4
