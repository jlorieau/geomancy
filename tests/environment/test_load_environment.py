"""Test env functions, regexes and utilities"""
import os
from pathlib import Path

import pytest

from geomancy.environment import parse_env_str, load_env


def test_parse_env_str_strip_comment():
    """Test the parse_env_str function with comment stripping"""
    parse = parse_env_str

    # Comment (#) is stripped to the end of the line
    assert parse("ENV = dev # development environment") == {"ENV": "dev"}

    # Escaped comment (\#) is not touched
    assert parse(r"ENV = dev \# development environment") == {
        "ENV": "dev \\# development environment"
    }


def test_parse_env_str_no_sub():
    """Test the parse_env_str function without substitution"""

    def parse(string):
        return parse_env_str(string, substitute=False)

    # Simple assignment
    assert parse("ENV=dev") == {"ENV": "dev"}
    assert parse("EMAIL=${USER}@example.org") == {"EMAIL": "${USER}@example.org"}

    # Single and double quotes
    assert parse("ENV='dev'") == {"ENV": "dev"}
    assert parse('ENV="dev"') == {"ENV": "dev"}

    # Mismatched quote don't work
    assert parse("ENV='dev\"") == {}
    assert parse("ENV=\"dev'") == {}

    # triple quotes
    assert parse("ENV='''dev'''") == {"ENV": "dev"}
    assert parse('ENV="""dev"""') == {"ENV": "dev"}

    # quote mixing is currently allowed
    assert parse("ENV='''dev'") == {"ENV": "''dev"}
    assert parse("ENV='dev'''") == {"ENV": "dev''"}

    # muliti-line quotes
    assert parse('ENV="""My first line\nMy second line"""') == {
        "ENV": "My first line\nMy second line"
    }

    # slashes
    assert parse("CACHE_DIR=${PWD}/cache") == {"CACHE_DIR": "${PWD}/cache"}


def test_parse_env_str_with_sub():
    """Test the parse_env_str function with substitution and loading"""

    def parse(string):
        return parse_env_str(string, substitute=True)

    assert parse("EMAIL_ADDRESS=${USER}@example.org") == {
        "EMAIL_ADDRESS": "{USER}@example.org".format(**os.environ)
    }

    assert parse("EMAIL=${MISSING}@example.org") == {"EMAIL": "${MISSING}@example.org"}


def test_load_env():
    """Test the load_env function using test.env"""
    with pytest.MonkeyPatch.context() as mp:
        # Clear the environment variables from 'test.env'
        for name in ("VALUE1", "VALUE2", "VALUE3"):
            mp.delenv(name, raising=False)

        # Load the environment variables from 'test.env'
        filepath = Path(__file__).parent / "test.env"
        count = load_env(filepath=filepath, overwrite=False)

        assert os.environ["VALUE1"] == "My Value"
        assert os.environ["VALUE2"] == "dev"
        assert os.environ["VALUE3"] == "my-dev"
        assert os.environ["VALUE4"] == "A Multiline\nenvironment variable"
        assert os.environ["VALUE5"] == "Extra endspaces removed"
        assert count == 5

        # The environment variables are already loaded, so trying so again
        # will give a loaded count = 0 -- i.e. no variables loaded
        count = load_env(filepath=filepath, overwrite=False)
        assert count == 0

        # Unless we put the overwrite flag, in which case the 5 variables will
        # be overwritten
        count = load_env(filepath=filepath, overwrite=True)
        assert count == 5
