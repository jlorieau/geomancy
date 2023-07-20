"""
Test the environment variable check class
"""
from geomancy.checks import CheckBase


def test_check_base_types_dict():
    """Test the CheckBase.types_dict() method."""

    types = CheckBase.types_dict()

    # All keys should be strings (class names)
    assert all(isinstance(k, str) for k in types.keys())

    # All values should be classes
    assert all(issubclass(v, CheckBase) or v == CheckBase
               for v in types.values())
