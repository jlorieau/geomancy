"""Tests for Check tree constructors from dicts."""
from pytest import MonkeyPatch

from geomancy.checks import CheckBase, CheckEnv
from geomancy.constructors.dict import construct_from_dict


def test_construct_from_dict_simple():
    """Test the construction of a check tree from a simple dict"""
    d = {'CheckEnv': 'PATH',
         'desc': 'Check the existence of the $PATH environment variable'}

    check = construct_from_dict(name='base check', d=d)

    assert check is not None
    assert isinstance(check, CheckEnv)
    assert check.value == 'PATH'
    assert check.desc == d['desc']


def test_construct_from_dict_nested():
    """Test the construction of a check tree from a nested dict"""
    d = {'Environment':
         {'desc': 'Environment checks',
          'checkPath': {'checkEnv': 'VAR1', 'desc': 'Check VAR2'},
          'checkTerm': {'checkEnv': 'VAR2', 'desc': 'Check VAR2'}}
         }

    check = construct_from_dict(name='base check', d=d)

    # Validate the root check
    assert check is not None
    assert isinstance(check, CheckBase)
    assert check.name == 'base check'

    # Validate the check tree
    flattened = check.flatten()
    assert len(flattened) == 4

    # Validate class types
    assert flattened[0].__class__ == CheckBase
    assert flattened[1].__class__ == CheckBase
    assert flattened[2].__class__ == CheckEnv
    assert flattened[3].__class__ == CheckEnv

    # Validate check names
    assert flattened[0].name == 'base check'
    assert flattened[1].name == 'Environment'
    assert flattened[2].name == 'checkPath'
    assert flattened[3].name == 'checkTerm'

    # Validate check values
    assert flattened[0].value is None
    assert flattened[1].value is None
    assert flattened[2].value == 'VAR1'
    assert flattened[3].value == 'VAR2'

    # Validate sub_check entries
    assert flattened[0].sub_checks == [flattened[1]]
    assert flattened[1].sub_checks == [flattened[2], flattened[3]]
    assert flattened[2].sub_checks == []
    assert flattened[3].sub_checks == []

    # Validate that check is correct
    with MonkeyPatch.context() as mp:
        # Set the environment variables so that the overall check passes
        mp.setenv('VAR1', 'value 1')
        mp.setenv('VAR2', 'value 2')

        assert check.check()

        # Remove the environment variables so that the overall check fails
        mp.delenv('VAR1')
        mp.delenv('VAR2')

        assert not check.check()
