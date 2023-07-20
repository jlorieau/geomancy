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

    # Try checking the values on the config object, the A class attribute and
    # the A instance attribute
    assert config.value1 == 'new value1'
    assert config.value2 == 4
    assert A.attribute1 == 'new value1'
    assert A.attribute2 == 4
    assert a.attribute1 == 'new value1'
    assert a.attribute2 == 4

    # Try modifying the values on the class attributes
    a.attribute1 = 'very new value1'
    a.attribute2 = 5

    # Try checking the new values on the config object, the A class attribute
    # and the A instance attribute
    assert config.value1 == 'very new value1'
    assert config.value2 == 5
    assert A.attribute1 == 'very new value1'
    assert A.attribute2 == 5
    assert a.attribute1 == 'very new value1'
    assert a.attribute2 == 5


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

    # Try measuring the values directly on the Config singleton and the
    # class/instance attributes
    assert config.general.value1 == 'value 1'
    assert config.general.value2 == 2
    assert A.attribute1 == 'value 1'
    assert A.attribute2 == 2
    assert a.attribute1 == 'value 1'
    assert a.attribute2 == 2

    # Try modifying the values on the Config
    config.general.value1 = 'new value 1'
    config.general.value2 = 3

    # Try measuring the values directly on the Config singleton and the
    # class/instance attributes
    assert config.general.value1 == 'new value 1'
    assert config.general.value2 == 3
    assert A.attribute1 == 'new value 1'
    assert A.attribute2 == 3
    assert a.attribute1 == 'new value 1'
    assert a.attribute2 == 3

    # Try modifying the values on the instance
    a.attribute1 = "very new value 1"
    a.attribute2 = 4

    # Try measuring the values directly on the Config singleton and the
    # class/instance attributes
    assert config.general.value1 == 'very new value 1'
    assert config.general.value2 == 4
    assert A.attribute1 == 'very new value 1'
    assert A.attribute2 == 4
    assert a.attribute1 == 'very new value 1'
    assert a.attribute2 == 4
