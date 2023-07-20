"""Test the config module"""
import tomllib
from pathlib import Path

import pytest

from geomancy.config.config import Config, Parameter

@pytest.fixture
def reset_config():
    """Reset the Config singleton"""
    if Config._instance is not None:
        Config._instance = None


def test_config_getset(reset_config):
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


def test_config_nested(reset_config):
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

    # Check the nested dict in Config - level 1
    assert isinstance(config.__dict__, dict)
    assert len(config.__dict__) == 1

    # Check the nested dict in Config - level 2
    assert len(config.__dict__['general']) == 2
    assert isinstance(config.__dict__['general'], Config)

    # Check the nested dict in Config - level 3
    assert len(config.__dict__['general'].__dict__) == 2
    assert config.__dict__['general'].__dict__['value1'] == 'value 1'
    assert config.__dict__['general'].__dict__['value2'] == 2

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


def test_toml_parsing(reset_config):
    """Test Config with the parsing of TOML strings and files"""
    # Load the toml file
    filename = Path(__file__).parent / 'config1.toml'
    config = Config()
    config.toml_load(filename)

    config.pprint()
    # Check the parsed config
    assert config.checkEnv.env_substitute
    assert config.checkEnv.msg == "A test message"
    assert config.checkEnv.value.nested == 1
