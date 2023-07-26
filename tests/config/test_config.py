"""Test the config module"""
from pathlib import Path

import pytest

from geomancy.config.config import ConfigException, Config, Parameter


@pytest.fixture
def reset_config():
    """Reset the Config singleton"""
    # noinspection PyProtectedMember
    if Config._instance is not None:
        Config._instance = None


def test_config_allowed_keys(reset_config):
    """Tests allowed key for Config entries"""
    config = Config()
    valid_keys = ("test1", "TEST1", "TEST_1", "_TEST1")
    invalid_keys = ("test 1", " test1", "test.1")

    for key in valid_keys:
        setattr(config, key, "value")

    for key in invalid_keys:
        with pytest.raises(ConfigException):
            setattr(config, key, "value")


def test_config_getset(reset_config):
    """Test the Config and Parameter get/set methods"""

    config = Config(value1="value1", value2=3)

    class A:
        attribute1 = Parameter("value1")
        attribute2 = Parameter("value2")

    a = A()

    # Try measuring the values directly
    assert config.value1 == "value1"
    assert config.value2 == 3
    assert a.attribute1 == "value1"
    assert a.attribute2 == 3

    # Try modifying the values on the config
    config.value1 = "new value1"
    config.value2 = 4

    # Try checking the values on the config object, the A class attribute and
    # the A instance attribute
    assert config.value1 == "new value1"
    assert config.value2 == 4
    assert A.attribute1 == "new value1"
    assert A.attribute2 == 4
    assert a.attribute1 == "new value1"
    assert a.attribute2 == 4

    # Try modifying the values on the class attributes
    a.attribute1 = "very new value1"
    a.attribute2 = 5

    # Try checking the new values on the config object, the A class attribute
    # and the A instance attribute
    assert config.value1 == "very new value1"
    assert config.value2 == 5
    assert A.attribute1 == "very new value1"
    assert A.attribute2 == 5
    assert a.attribute1 == "very new value1"
    assert a.attribute2 == 5


def test_config_default(reset_config):
    """Test the Config and Parameter with hard-coded default values."""

    # Try creating attributes with defaults
    class A:
        attribute1 = Parameter("A.attribute1", default="default value")
        attribute2 = Parameter("A.attribute2", default=3)

    # Check that these values were placed in the config
    config = Config()
    assert config.A.attribute1 == "default value"
    assert config.A.attribute2 == 3

    # Try changing the config values and see if those changes have been
    # reflected in the config
    config.A.attribute1 = "new default value"
    config.A.attribute2 = 4

    # The class values should be changed
    assert A.attribute1 == "new default value"
    assert A.attribute2 == 4


def test_config_nested(reset_config):
    """Test the Config and Parameter with nested attributes"""
    config = Config()

    # Try modifying the config
    config.general.value1 = "value 1"
    config.general.value2 = 2

    # Try accessing through class properties
    class A:
        attribute1 = Parameter("general.value1")
        attribute2 = Parameter("general.value2")

    a = A()

    # Check the nested dict in Config - level 1
    assert isinstance(config.__dict__, dict)
    assert len(config.__dict__) == 1

    # Check the nested dict in Config - level 2
    assert len(config.__dict__["general"]) == 2
    assert isinstance(config.__dict__["general"], Config)

    # Check the nested dict in Config - level 3
    assert len(config.__dict__["general"].__dict__) == 2
    assert config.__dict__["general"].__dict__["value1"] == "value 1"
    assert config.__dict__["general"].__dict__["value2"] == 2

    # Try measuring the values directly on the Config singleton and the
    # class/instance attributes
    assert config.general.value1 == "value 1"
    assert config.general.value2 == 2
    assert A.attribute1 == "value 1"
    assert A.attribute2 == 2
    assert a.attribute1 == "value 1"
    assert a.attribute2 == 2

    # Try modifying the values on the Config
    config.general.value1 = "new value 1"
    config.general.value2 = 3

    # Try measuring the values directly on the Config singleton and the
    # class/instance attributes
    assert config.general.value1 == "new value 1"
    assert config.general.value2 == 3
    assert A.attribute1 == "new value 1"
    assert A.attribute2 == 3
    assert a.attribute1 == "new value 1"
    assert a.attribute2 == 3

    # Try modifying the values on the instance
    a.attribute1 = "very new value 1"
    a.attribute2 = 4

    # Try measuring the values directly on the Config singleton and the
    # class/instance attributes
    assert config.general.value1 == "very new value 1"
    assert config.general.value2 == 4
    assert A.attribute1 == "very new value 1"
    assert A.attribute2 == 4
    assert a.attribute1 == "very new value 1"
    assert a.attribute2 == 4


def test_config_recursive_update(reset_config):
    """Test the recursive update"""
    values = {
        "section1": {"subsection1": 1, "subsection2": 2},
        "section2": 3,
        "section3": 4,
    }
    updates = {
        "section1": {"subsection2": -2},
        "section2": -3,
        "section4": {"subsection4": 5},
    }
    bad_updates = {"section1": 0}  # Replace a section with a value

    # Create and check the reference config
    config = Config.load(values)

    assert config.section1.subsection1 == 1
    assert config.section1.subsection2 == 2
    assert config.section2 == 3
    assert config.section3 == 4

    # Introduce updates and check new values
    config.update(updates)

    assert config.section1.subsection1 == 1
    assert config.section1.subsection2 == -2  # new value
    assert config.section2 == -3  # new value
    assert config.section3 == 4
    assert config.section4.subsection4 == 5  # new section

    # Try a bad update that eliminates a section
    with pytest.raises(ConfigException):
        config.update(bad_updates)

    assert config.section1.subsection1 == 1  # config remains


@pytest.mark.parametrize(
    "ext,save_file",
    (
        ("toml", False),
        ("toml", True),
        ("yaml", False),
        ("yaml", True),
    ),
)
def test_config_parsing_strings(reset_config, tmp_path, ext, save_file):
    """Test Config load/dump string methods"""
    # Setup a config
    config = Config()
    config.a = 1
    config.b = "string"
    config.c = True
    config.d.a = "subsection1"
    config.d.b = "subsection2"

    # Create a string from the default config
    dict_copy = dict(config.__dict__)
    assert len(dict_copy) == 4  # 'a', 'b', 'c'  and 'd'

    # Create a string from the config
    meth = getattr(config, f"dumps_{ext}")
    config_str = meth()
    assert config_str.strip() != ""

    # Optionally save the string to a file
    if save_file:
        filepath = (tmp_path / "test").with_stem("." + ext)
        filepath.write_text(config_str)
    else:
        filepath = None

    Config._instance = None  # reset singleton

    # Try reloading the string
    if save_file:
        meth = getattr(Config, f"load_{ext}")
        new_config = meth(filepath)
    else:
        meth = getattr(Config, f"loads_{ext}")
        new_config = meth(config_str)

    # Make sure the new dict matches the old
    assert len(dict_copy) == 4 and len(new_config.__dict__) == 4
    assert dict_copy == new_config.__dict__


def test_config_toml_parsing(reset_config):
    """Test Config with the parsing of TOML strings and files"""
    # Load the toml file
    filename = Path(__file__).parent / "config1.toml"
    config = Config.load_toml(filename)

    # Check the parsed config
    assert config.checkEnv.env_substitute
    assert config.checkEnv.msg == "A test message"
    assert config.checkEnv.value.nested == 1
