"""
Test the environment variable check class
"""
from geomancy.checks import CheckBase


def test_check_base_flatten():
    """Test the CheckBase.flatten() method"""
    # Create a CheckBase tree
    sub11 = CheckBase(name='sub11')
    sub12 = CheckBase(name='sub12')
    sub1 = CheckBase(name='sub1', sub_checks=[sub11, sub12])
    sub2 = CheckBase(name='sub2')
    root = CheckBase(name='root', sub_checks=[sub1, sub2])

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
    assert all(issubclass(v, CheckBase) or v == CheckBase
               for v in types.values())
