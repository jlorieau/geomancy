"""Test check utilities"""
from pytest import MonkeyPatch

from geomancy.checks.utils import sub_env


def test_sub_env():
    """Test the sub_env environment substitution."""

    with MonkeyPatch.context() as mp:
        mp.setenv("VAR1", "variable1")
        mp.setenv("VAR2", "variable2")
        mp.delenv("MISSING", raising=False)

        # Test with strings
        assert sub_env("{VAR1}") == "variable1"
        assert sub_env("{VAR2}") == "variable2"
        assert sub_env("{MISSING}") is None

        # Test with tuples
        assert sub_env(("{VAR1}", "{VAR2}")) == ("variable1", "variable2")

        # Test with lists
        assert sub_env(["{VAR1}", "{VAR2}"]) == ["variable1", "variable2"]

        # Test with dicts and dict-likes
        assert sub_env({"{VAR1}": "{VAR2}"}) == {"variable1": "variable2"}
