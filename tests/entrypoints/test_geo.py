"""Test the main CLI entrypoint"""
import typing as t
from pathlib import Path
from itertools import chain
import os

from click.testing import CliRunner
import pytest

from geomancy.entrypoints import geo_cli
from geomancy.config import Config


@pytest.fixture
def run() -> t.Callable:
    """Run the CLI with the given option, check for the expected exit
    code and return the output"""

    def runcmd(args, expected_code: int = 0):
        args = [args] if isinstance(args, str) else args

        runner = CliRunner()
        result = runner.invoke(geo_cli, args)
        if result.exit_code != expected_code:
            print(result.output)
        assert result.exit_code == expected_code
        return result

    runcmd.__doc__ = run.__doc__
    return runcmd


@pytest.fixture
def config() -> Config:
    return Config()


@pytest.mark.parametrize("options", ("--help",))
def test_cli_help(run, options):
    """Test the --help message"""
    result = run(options)
    assert "Show this message and exit" in result.output


@pytest.mark.parametrize(
    "options",
    chain(*tuple(Path("examples").glob(f"*.{ext}") for ext in ("toml", "yaml"))),
)
def test_cli_check(run, options):
    """Test CLI with all the checks files individually in the examples directory"""
    result = run(str(options))

    # Check, for example, that environment variables were checked
    assert any(
        msg in result.output for msg in ("Check environment variable", "Check path")
    )


@pytest.mark.parametrize("options", ("examples/geomancy.*",))
def test_cli_check_glob(run, options):
    """Test the CLI with glob patterns"""
    result = run(str(options))

    # Check, for example, that environment variables were checked
    assert any(
        msg in result.output for msg in ("Check environment variable", "Check path")
    )


@pytest.mark.parametrize("flag", ("", "--toml", "--yaml"))
def test_cli_config(run, flag):
    """Test the --config option"""
    if flag:
        result = run(("config", flag))
    else:
        result = run(("config",))
    assert "config" in result.output  # config output in TOML/yaml format


@pytest.mark.parametrize("flag", ("-e", "--env"))
def test_cli_env(run, flag, test_env_file):
    """Test the -e/--env and --overwrite flags for loading environment
    variables.

    See ./conftest.py for details on the 'test_env_file' fixture
    """
    # running '--overwrite' without '-e/--env' gives an error
    result = run("--overwrite", expected_code=2)

    with pytest.MonkeyPatch.context() as mp:
        filepath = test_env_file["filepath"]
        variables = test_env_file["variables"]

        # Reset env variables
        for name in variables.keys():
            mp.delenv(name, raising=False)

        # running "-e/--env" should load environment variables, which are logged
        # in debug mode
        options = ("-d", flag, filepath)
        result = run(options)

        # The variables are loaded in the current process
        for name, value in variables.items():
            assert os.environ[name] == value
