"""Test dotenv functions, regexes and utilities"""
import os

import pytest

from geomancy.environment.dotenv import parse_dotenv_str


def test_parse_dotenv_str_strip_comment():
    """Test the parse_dotenv_str function with comment stripping"""
    parse = parse_dotenv_str

    # Comment (#) is stripped to the end of the line
    assert parse("ENV = dev # development environment") == {"ENV": "dev"}

    # Escaped comment (\#) is not touched
    assert parse(r"ENV = dev \# development environment") == {
        "ENV": "dev \\# development environment"
    }


def test_parse_dotenv_str_no_sub():
    """Test the parse_dotenv_str function without substitution"""

    def parse(string):
        return parse_dotenv_str(string, substitute=False)

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


@pytest.mark.parametrize("load", (True, False))
def test_parse_dotenv_str_with_sub(load):
    """Test the parse_dotenv_str function with substitution and loading"""

    def parse(string):
        return parse_dotenv_str(string, substitute=True, load=load)

    with pytest.MonkeyPatch.context() as mp:
        mp.delenv("EMAIL_ADDRESS", raising=False)  # Remove env variable
        assert "EMAIL_ADDRESS" not in os.environ

        # Simple assignment of the value
        assert parse("EMAIL_ADDRESS=${USER}@example.org") == {
            "EMAIL_ADDRESS": "{USER}@example.org".format(**os.environ)
        }

        # The value may be loaded in the environment
        if load:
            assert "EMAIL_ADDRESS" in os.environ
        else:
            assert "EMAIL_ADDRESS" not in os.environ

    # Try for a missing variable. It just isn't substituted
    with pytest.MonkeyPatch.context() as mp:
        mp.delenv("MISSING", raising=False)  # Temporarily remove env variable

        assert parse("EMAIL=${MISSING}@example.org") == {
            "EMAIL": "${MISSING}@example.org"
        }
