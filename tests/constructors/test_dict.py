"""Tests for Check tree constructors from dicts."""
from geomancy.checks import CheckEnv
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


def test_Construct_from_dict_nested():
    """Test the construction of a check tree from a nested dict"""