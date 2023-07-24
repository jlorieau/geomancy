"""Test dotenv functions, regexes and utilities"""
import os

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

    # assert get_match("EMAIL=${USER}@example.org") == {
    #     "EMAIL": "{USER}@example.org".format(**os.environ)
    # }  # simple substitution
