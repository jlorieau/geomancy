"""Test the config module"""
from geomancy.config.config import Config, Parameter


def test_config_getset():
    """Test the Config and Parameter get/set methods"""

    config = Config(value1='value1', value2=3)

    class A:
        attribute1 = Parameter('value1')
        attribute2 = Parameter('value2')
    a = A()

    # Try measuring the values directly
    assert config.value1 == 'value1'
    assert config.value2 == 3
    assert a.attribute1 == 'value1'
    assert a.attribute2 == 3

    # Try modifying the values on the config
    config.value1 = 'new value1'
    config.value2 = 4

    assert config.value1 == 'new value1'
    assert config.value2 == 4
    assert a.attribute1 == 'new value1'
    assert a.attribute2 == 4


def test_config_nested():
    """Test the Config and Parameter with nested attributes """
    config = Config()

    # Try modifying the config
    config.general.value1 = 'value 1'
    config.general.value2 = 2

    # Try accessing through class properties
    class A:
        attribute1 = Parameter('general.value1')
        attribute2 = Parameter('general.value2')
    a = A()

    # Try measuring the values directly on the Config singleton
    assert config.general.value1 == 'value 1'
    assert config.general.value2 == 2

    # Try measuring the values from class attributes
    assert A.attribute1 == 'value 1'
    assert A.attribute2 == 2
