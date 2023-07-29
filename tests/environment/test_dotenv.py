"""Test env functions, regexes and utilities"""
import os

import pytest

from geomancy.environment import sub_env, parse_env, load_env


def test_sub_env():
    """Test environment variable substitutions with sub_env"""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("VAR1", "variable1")
        mp.setenv("VAR2", "variable2")
        mp.delenv("MISSING", raising=False)

        # Test with braces and with $
        assert sub_env("${VAR1}") == "variable1"
        assert sub_env("${VAR2}") == "variable2"
        assert sub_env("${MISSING}") == ''

        # Test without braces and with $
        assert sub_env("$VAR1") == "variable1"
        assert sub_env("$VAR2") == "variable2"
        assert sub_env("$MISSING") == ''


def test_parse_env_docker_rules():
    """Test the parse_env function rules compared to docker dotenv rules.

    The layout and order of these tests deliberately matches the following:
    https://docs.docker.com/compose/environment-variables/env-file/#syntax
    """
    p = parse_env

    # Lines beginning with # are processed as comments and ignored
    assert p("# VAR=VAL") == {}
    assert p(" # VAR=VAL") == {}

    # Blank lines are ignored
    assert p("\n") == {}

    # Each line represents a key-value pair. Values can optionally be quoted
    assert p("VAR=VAL") == {"VAR": "VAL"}
    assert p('VAR="VAL"') == {"VAR": "VAL"}
    assert p("VAR='VAL'") == {"VAR": "VAL"}

    # Inline comments for unquoted values must be preceded with a space
    assert p("VAR=VAL # comment") == {"VAR": "VAL"}
    assert p("VAR=VAL# not a comment") == {"VAR": "VAL# not a comment"}

    # Inline comments for quoted values must follow the closing quote
    assert p('VAR="VAL # not a comment"') == {"VAR": "VAL # not a comment"}
    assert p('VAR="VAL" # comment') == {"VAR": "VAL"}

    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("OTHER", "NEWVALUE")

        # Single-quoted (') values are used literally.
        assert p("VAR='$OTHER'") == {"VAR": "$OTHER"}
        assert p("VAR='${OTHER}'") == {"VAR": "${OTHER}"}

        # Double-quote (") values allow substitution
        assert p(r'VAR="My ${OTHER}."') == {"VAR": "My NEWVALUE."}

    # Quotes can be escaped with a backslash: \' or \"
    assert p(r"VAR='Let\'s go!'") == {"VAR": r"Let's go!"}
    assert p(r'VAR="{\"hello\": \"json\"}"') == {"VAR": r'{"hello": "json"}'}

    # Common shell escape sequences including \n, \r, \t, and \\ are supported
    # in double-quoted values.
    assert p(r'VAR="some\tvalue"') == {"VAR": "some\tvalue"}
    assert p(r"VAR='some\tvalue'") == {"VAR": r"some\tvalue"}
    assert p(r"VAR=some\tvalue") == {"VAR": r"some\tvalue"}


def test_parse_env_docker_parameter_expansion():
    """Test the parse_env_str function parameter expansion compared to docker
    dotenv parameter expansion.

    The layout and order of these tests deliberately matches the following:
    https://docs.docker.com/compose/environment-variables/env-file/#parameter-expansion
    """
    p = parse_env

    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("OTHER_VAL", "new value")

        # Direct substitution (braced)
        assert p(r"VAR=${OTHER_VAL}") == {"VAR": "new value"}  # (un-quoted)
        assert p(r'VAR="${OTHER_VAL}"') == {"VAR": "new value"}  # (double quoted)
        assert p(r"VAR='${OTHER_VAL}'") == {"VAR": "${OTHER_VAL}"}  # (literal)

        # Direct substitution (unbraced)
        assert p(r"VAR=$OTHER_VAL") == {"VAR": "new value"}  # (un-quoted)
        assert p(r'VAR="$OTHER_VAL"') == {"VAR": "new value"}  # (double quoted)
        assert p(r"VAR='$OTHER_VAL'") == {"VAR": "$OTHER_VAL"}  # (literal)

        # Default value
        assert p(r"VAR=${MISSING:-my default value}") == {"VAR": "my default value"}
        assert p(r"VAR=${MISSING-my default value}") == {"VAR": "my default value"}
        assert p(r"VAR=$MISSING:-default") == {"VAR": "default"}
        assert p(r"VAR=$MISSING-default") == {"VAR": "default"}

        # Error value
        for error_value in (
            r"VAR=${ERROR:?error raised}",
            r"VAR=${ERROR?error raised}",
            r"VAR=$ERROR:?error",
            r"VAR=$ERROR?error",
        ):
            with pytest.raises(EnvironmentError) as e:
                p(error_value)

        # Replace value
        assert p(r"VAR=${OTHER_VAL:+replaced value}") == {"VAR": "replaced value"}
        assert p(r"VAR=${OTHER_VAL+replaced value}") == {"VAR": "replaced value"}
        assert p(r"VAR=$OTHER_VAL:+replaced") == {"VAR": "replaced"}
        assert p(r"VAR=$OTHER_VAL+replaced") == {"VAR": "replaced"}

        assert p(r"VAR=${MISSING:+replaced value}") == {"VAR": ""}
        assert p(r"VAR=${MISSING+replaced value}") == {"VAR": ""}
        assert p(r"VAR=$MISSING:+replaced") == {"VAR": ""}
        assert p(r"VAR=$MISSING+replaced") == {"VAR": ""}


def test_load_env(test_env_file):
    """Test the load_env function using test.env.

    See ../conftest.py for details on the 'test_env_file' fixture
    """
    with pytest.MonkeyPatch.context() as mp:
        filepath = test_env_file["filepath"]
        variables = test_env_file["variables"]

        # Clear the environment variables from 'test.env'
        for name in variables.keys():
            mp.delenv(name, raising=False)

        # Load the environment variables from 'test.env'
        env_vars = load_env(filepath=filepath, overwrite=False)

        for name, value in variables.items():
            assert os.environ[name] == value
        assert len(env_vars) == len(variables)

        # The environment variables are already loaded, so trying so again
        # will give a loaded count = 0 -- i.e. no variables loaded
        env_vars = load_env(filepath=filepath, overwrite=False)
        assert len(env_vars) == 0

        # Unless we put the overwrite flag, in which case the 5 variables will
        # be overwritten
        env_vars = load_env(filepath=filepath, overwrite=True)
        assert len(env_vars) == len(variables)
