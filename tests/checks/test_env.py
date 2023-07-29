"""
Test the environment variable check class
"""
import os

from pytest import MonkeyPatch

from geomancy.checks import CheckEnv


def test_check_env_missing():
    """Test CheckEnv for a missing environment variable"""
    with MonkeyPatch.context() as mp:
        mp.delenv("MISSING", raising=False)
        check = CheckEnv(name="missing", value="${MISSING}")
        assert not check.check().passed


def test_check_env_present():
    """Test CheckEnv for a present environment variable"""
    with MonkeyPatch.context() as mp:
        mp.setenv("PRESENT", "VALUE")

        check = CheckEnv(name="PRESENT", value="${PRESENT}")
        assert check.name == "PRESENT"
        assert check.value == "VALUE"
        assert check.check().passed


def test_check_env_name_substitution(
    variable_name="VARIABLE_NAME", variable_value="PATH"
):
    """Test CheckEnv with substituting variable names with environment
    variables"""
    # Set the VariableName environment variable to be the name of another
    # environment variable that exists
    with MonkeyPatch.context() as mp:
        mp.setenv(variable_name, variable_value)

        # Setup the check to use the variable name with environment variable
        # substitution--i.e. wrap it in curly braces
        check = CheckEnv(name="substitution", value=f"${variable_name}")

        # Check that the subsitution is correct
        assert check.name == "substitution"
        assert check.raw_value == f"${variable_name}"  # unprocessed value
        assert check.value == variable_value

        assert check.check().passed


def test_check_env_regex(
    variable_name="VARIABLE_NAME", variable_value="dev", regex="dev|prod|local"
):
    # Make sure the variable name isn't in the environment already
    assert variable_name not in os.environ

    # Place the variable in the environment and test the regex
    with MonkeyPatch.context() as mp:
        mp.setenv(variable_name, variable_value)

        # The regex should match
        check1 = CheckEnv(name="regex1", value=f"${variable_name}", regex=regex)
        assert check1.check().passed

        # Change the variable value to something else in which the regex will
        # fail
        mp.setenv(variable_name, f"!{variable_value}!")

        # The regex should not match
        check2 = CheckEnv(name="regex2", value=f"${variable_name}", regex=regex)
        assert not check2.check().passed


def test_check_base_types_dict():
    """Test the CheckBase.types_dict() method for the CheckEnv class."""
    types = CheckEnv.types_dict()

    # Verify CheckEnv entries and aliases
    assert types["CheckEnv"] == CheckEnv
    assert types["checkEnv"] == CheckEnv
