"""
Test the environment variable check class
"""
from geomancy.checks import CheckBase


# A dummy CheckBase subclass for tests
class CheckDummy(CheckBase):
    aliases = ("checkDummy",)


def test_check_base_flatten():
    """Test the CheckBase.flatten() method"""
    # Create a CheckBase tree
    sub11 = CheckBase(name="sub11")
    sub12 = CheckBase(name="sub12")
    sub1 = CheckBase(name="sub1", children=[sub11, sub12])
    sub2 = CheckBase(name="sub2")
    root = CheckBase(name="root", children=[sub1, sub2])

    # Check the flattened tree
    flattened = root.flatten()

    assert len(flattened) == 5
    assert flattened[0] == root
    assert flattened[1] == sub1
    assert flattened[2] == sub11
    assert flattened[3] == sub12
    assert flattened[4] == sub2


def test_check_base_types_dict():
    """Test the CheckBase.types_dict() method"""

    types = CheckBase.types_dict()

    # All keys should be strings (class names)
    assert all(isinstance(k, str) for k in types.keys())

    # All values should be classes
    assert all(issubclass(v, CheckBase) or v == CheckBase for v in types.values())


def test_check_base_load_simple():
    """Test the CheckBase load method from a simple dict"""
    d = {"CheckDummy": "PATH", "desc": "The $PATH environment variable"}

    check = CheckBase.load(d=d, name="base check")

    assert check is not None
    assert isinstance(check, CheckBase)
    assert check.__class__ == CheckDummy
    assert check.value == "PATH"
    assert check.desc == d["desc"]


def test_check_base_load_nested():
    """Test the CheckBase load method from a nested dict"""
    d = {
        "Environment": {
            "desc": "Environment checks",
            "Path": {"checkDummy": "VAR1", "desc": "Check VAR2"},
            "Term": {"checkDummy": "VAR2", "desc": "Check VAR2"},
        }
    }

    check = CheckBase.load(d=d, name="base check")

    # Validate the root check
    assert check is not None
    assert isinstance(check, CheckBase)
    assert check.name == "base check"

    # Validate the check tree
    flattened = check.flatten()
    assert len(flattened) == 4

    # Validate class types
    assert flattened[0].__class__ == CheckBase
    assert flattened[1].__class__ == CheckBase
    assert flattened[2].__class__ == CheckDummy
    assert flattened[3].__class__ == CheckDummy

    # Validate check names
    assert flattened[0].name == "base check"
    assert flattened[1].name == "Environment"
    assert flattened[2].name == "Path"
    assert flattened[3].name == "Term"

    # Validate check values
    assert flattened[0].value is None
    assert flattened[1].value is None
    assert flattened[2].value == "VAR1"
    assert flattened[3].value == "VAR2"

    # Validate children entries
    assert flattened[0].children == [flattened[1]]
    assert flattened[1].children == [flattened[2], flattened[3]]
    assert flattened[2].children == []
    assert flattened[3].children == []
