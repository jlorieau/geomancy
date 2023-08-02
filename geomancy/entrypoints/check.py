"""
The 'check' subcommand
"""
import typing as t
import logging
import tomllib
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack

import click
from rich.live import Live
import yaml
import vcr

from .environment import env_options
from .utils import filepaths
from ..checks import Check
from ..config import Config

__all__ = ("check",)

# Setup logger and configuration
logger = logging.getLogger(__name__)


# Exception classes
class MissingChecks(click.ClickException):
    """No checks were found in the checks files"""


# Config options
config = Config()
config.CLI.CHECKS_PATHS = [  # Default paths for checks files
    "pyproject.toml",
    ".geomancy.??ml",
    "geomancy.??ml",
    "geomancy.yml",
    ".geomancy.yml",
]
config.CLI.TOML_EXTS = [".toml"]  # Default file extensions for TOML files
config.CLI.YAML_EXTS = [".yml", ".yaml"]  # Default file extensions for YAML files
config.CLI.VCR.RECORD_MODE = "ONCE"  # record fixtures if they don't exist
config.CLI.VCR.ADDITIONAL_FILTER_HEADERS = []


def validate_checks_files(
    ctx: click.Context, param: click.Parameter, values: t.Tuple[str]
):
    """Validate the checks files arguments and convert to valid paths"""
    # Convert filepath strings into Path objects. Use default locations if
    # no checks_files were specified (i.e. it is an empty list)
    existing_files = []
    for path in values or config.CLI.CHECKS_PATHS:
        existing_files += filepaths(path)

    # Nothing to do if no checks files were found
    if len(existing_files) == 0:
        raise click.MissingParameter(
            "Could not find a checks file.", ctx=ctx, param=param
        )
    logging.debug(f"Checking the following files: {existing_files}")
    return existing_files


# Setup 'check' command
@click.command
@env_options
@click.option(
    "-f",
    "--fixture",
    required=False,
    type=click.Path(),
    help="Fixture to replace network requests",
)
@click.argument("checks_files", nargs=-1, type=str, callback=validate_checks_files)
def check(checks_files, env, fixture):
    """Run checks"""
    logger.debug(f"check_files={checks_files}, env={env}, fixture={fixture}")

    # Convert the checks_files into checks
    checks = []
    for checks_file in checks_files:
        # Parse the file by filetype
        if checks_file.suffix in config.CLI.TOML_EXTS:
            with open(checks_file, "rb") as f:
                d = tomllib.load(f)

        elif checks_file.suffix in config.CLI.YAML_EXTS:
            with open(checks_file, "r") as f:
                d = yaml.load(f, Loader=yaml.SafeLoader)

        else:
            continue

        # pyproject.toml files have their items placed under the [tool.geomancy]
        # section
        if checks_file.name == "pyproject.toml":
            d = d.get("tool", dict()).get("geomancy", dict())

        # Load config section, if available
        for config_name in config.section_aliases:
            config_section = d.pop(config_name, None)
            if isinstance(config_section, dict):
                config.update(config_section)

        # Load the rest into a root CheckBase
        check = Check.load(d, name=str(checks_file))
        if check is not None:
            checks.append(check)

    # Create a root check, if there are a lot of checks
    if len(checks) > 1:
        check = Check(name=f"Checking {len(checks)} files", children=checks)
    elif len(checks) == 1:
        check = checks[0]
    else:
        plural = True if len(checks_files) > 1 else False
        raise MissingChecks(
            f"No checks were found in the file{'s' if plural else ''}: "
            f"{', '.join(map(str, checks_files))}."
        )

    with ExitStack() as stack:
        # Set up the context managers
        executor = stack.enter_context(ThreadPoolExecutor())  # concurrent.futures
        live = stack.enter_context(Live(refresh_per_second=4))  # rich live display

        if fixture is not None:
            # Request header items to remove before saving
            filter_headers = {
                "Authorization",
                "User-Agent",
                "X-Amz-Content-SHA256",
                "X-Amz-Date",
                "amz-sdk-invocation-id",
                "amz-sdk-request",
            }
            filter_headers.update(config.CLI.VCR.ADDITIONAL_FILTER_HEADERS)
            kwargs = {
                "record_mode": config.CLI.VCR.RECORD_MODE,
                "filter_headers": list(filter_headers),
            }

            stack.enter_context(vcr.use_cassette(fixture, **kwargs))  # vcr fixtures

        # Run the checks, display the results to the terminal
        result = check.check(executor=executor)

        # Update the display until the checks are done
        while not result.done:
            time.sleep(0.5)
            live.update(result.rich_table())

        # Print the final table
        live.update(result.rich_table())

    if not result.passed:
        exit(1)

    return result.passed
