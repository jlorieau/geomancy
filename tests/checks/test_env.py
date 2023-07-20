"""
Test the environment variable check class
"""
import os

from pytest import MonkeyPatch

from geomancy.checks import CheckEnv


def test_check_env_missing(variable_name='missingVariable'):
    """Test CheckEnv for a missing environment variable"""
    assert variable_name not in os.environ

    check = CheckEnv(name='missing', value=variable_name)
    assert not check.check()


def test_check_env_present(variable_name='PATH'):
    """Test CheckEnv for a present environment variable"""
    assert variable_name in os.environ

    check = CheckEnv(name='present', value=variable_name)
    assert check.check()


def test_check_env_name_substitution(variable_name='VARIABLE_NAME',
                                     variable_value='PATH'):
    """Test CheckEnv with substituting variable names with environment
    variables"""
    # Make sure the variable name isn't in the environment already
    assert variable_name not in os.environ
    assert '{' + variable_name + '}' not in os.environ

    # Set the VariableName envinronment variable to be the name of another
    # environment variable that exists
    with MonkeyPatch.context() as mp:
        mp.setenv(variable_name, variable_value)

        # Setup the check to use the variable name with environment variable
        # substitution--i.e. wrap it in curly braces
        check = CheckEnv(name='substitution',
                         value='{' + variable_name + '}')

        # Check that the subsitution is correct
        assert check.variable_name == 'PATH'
        assert check.value == '{' + variable_name + '}'  # hidden var

        assert check.check()


def test_check_env_regex(variable_name='VARIABLE_NAME',
                         variable_value='dev',
                         regex='dev|prod|local'):
    # Make sure the variable name isn't in the environment already
    assert variable_name not in os.environ

    # Place the variable in the environment and test the regex
    with MonkeyPatch.context() as mp:
        mp.setenv(variable_name, variable_value)

        # The regex should match
        check1 = CheckEnv(name='regex1', value=variable_name,
                          regex=regex)
        assert check1.check()

        # Change the variable value to something else in which the regex will
        # fail
        mp.setenv(variable_name, '!' + variable_value + '!')

        # The regex should not match
        check2 = CheckEnv(name='regex2', value=variable_name,
                          regex=regex)
        assert not check2.check()


def test_check_base_types_dict():
    """Test the CheckBase.types_dict() method for the CheckEnv class."""
    types = CheckEnv.types_dict()

    # Verify CheckEnv entries and aliases
    assert types['CheckEnv'] == CheckEnv
    assert types['checkEnv'] == CheckEnv
