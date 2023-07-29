"""
The 'check' subcommand
"""
import typing as t
import sys
import logging
import tomllib

import click
import yaml

from .environment import env_options
from .utils import filepaths
from ..checks import CheckBase
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
@click.argument("checks_files", nargs=-1, type=str, callback=validate_checks_files)
@env_options
def check(checks_files, env):
    """Run checks"""
    logger.debug(f"check_files={checks_files}")

    # Convert the checks_files into root checks
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
        check = CheckBase.load(d, name=str(checks_file))
        if check is not None:
            checks.append(check)

    # Create a root check, if there are a lot of checks
    if len(checks) > 1:
        checks = [CheckBase(name=f"Checking {len(checks)} files", children=checks)]
    elif len(checks) == 0:
        plural = True if len(checks_files) > 1 else False
        raise MissingChecks(
            f"No checks were found in the file{'s' if plural else ''}: "
            f"{', '.join(map(str, checks_files))}."
        )

    # Run the checks
    passed = all(check.check().passed for check in checks)
    if not passed:
        exit(1)

    return passed
