"""Test the main CLI entrypoint"""
import typing as t

import pytest

from geomancy.main import main_cli
from geomancy.config import Config


@pytest.fixture
def run(capsys) -> t.Callable:
    """Run the CLI with the given option, check for the expected exit
    code and return the output"""

    def runcmd(options, expected_code: int = 0):
        options = [options] if isinstance(options, str) else options
        try:
            main_cli(options)
        except SystemExit as e:
            if e.code != expected_code:
                raise e
        return capsys.readouterr()

    runcmd.__doc__ = run.__doc__
    return runcmd


@pytest.fixture
def config() -> Config:
    return Config()


@pytest.mark.parametrize("options", ("-h", "--help"))
def test_cli_help(run, options):
    """Test the --help message"""
    captured = run(options)
    assert "show this help message" in captured.out


@pytest.mark.parametrize("options", ("--disable-color",))
def test_cli_disable_color(run, options, config):
    """Test the --disable-color option"""
    captured = run(options)
    assert not config.TERM.USE_COLOR  # flag set to false


@pytest.mark.parametrize("options", ("--config",))
def test_cli_config(run, options):
    """Test the --config option"""
    captured = run(options)
    assert "[config]" in captured.out  # config output in TOML format


@pytest.mark.parametrize(
    "options", ("examples/geomancy.toml", "examples/pyproject.toml")
)
def test_cli_check(run, options):
    """Test the default checks"""
    captured = run(options)
    # Check environment variables
    assert "Check environment variable" in captured.out
