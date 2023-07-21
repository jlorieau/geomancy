"""
The program entry point.

This file is located in the root module directory, rather than the 'cli'
submodule because it may access functionality from all submodules
"""
import typing as t
import argparse
import logging
from pathlib import Path
import tomllib

from . import get_version, __description__
from .config import Config
from .checks import CheckBase

logger = logging.getLogger(__name__)  # Create a default logger
config = Config()  # Set up config defaults for the CLI

# Default paths for checks files
config.CLI.CHECKS_PATHS = [".geomancer.toml", "geomancer.toml"]

# Default paths for settings
config.CLI.SETTINGS_PATHS = ["{HOME}/.geomancerrc"]


def filepath(string: str, required: bool = True) -> t.Union["Path", None]:
    """Given a path string, verifies that the path is an existing file and
    converts it to a path.

    Parameters
    ----------
    string
        The path string to verify and convert
    required
        If True, log an error and exit the program if the file does not exist

    Returns
    -------
    path
        The path for the existing file
    """
    path = Path(string)
    if not path.is_file():
        if required:
            logger.error(f"Could not find the file given by the path {string}")
            exit(1)
        return None
    return path


def setup_parser() -> argparse.ArgumentParser:
    """Commands to set up the CLI parser"""
    # Create the parser
    parser = argparse.ArgumentParser(description=__description__)

    # Load custom files with checks
    parser.add_argument(
        "checks_files",
        type=filepath,
        nargs="*",
        help="Optional file containing checks to run",
    )

    parser.add_argument(
        "--disable-color", action="store_true", help="Disable colors in the terminal"
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s " + get_version(),
        help="Print the current version",
    )

    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    return parser


def setup_logging(debug: bool = False):
    """Set up the default logging"""
    logging.basicConfig(
        level=logging.DEBUG if debug else None,
        format="%(name)s:%(levelname)s: %(message)s",
    )


def get_checks(args: argparse.Namespace, required: bool = True) -> t.List["CheckBase"]:
    """Retrieve the list of parsed checks files from the given parsed
    arguments

    Parameters
    ----------
    args
        The parsed CLI arguments
    required
        If True, log an error and exit the program if no files were found
    """
    # Check the specified files
    if len(args.checks_files) > 0:
        # Use the specified checks_files, if available
        checks_files = args.checks_files
    else:
        # Otherwise use the default paths in the config
        checks_files = [filepath(p, required=False) for p in config.CLI.CHECKS_PATHS]
        checks_files = [p for p in checks_files if p is not None]

    # Nothing to do if no checks files were found
    if required and len(checks_files) == 0:
        logger.error(f"Could not find a checks file")
        exit(1)

    # Convert the checks_files into root checks
    checks = []
    for checks_file in checks_files:
        # Parse the file by filetype
        if checks_file.suffix in (".toml",):
            with open(checks_file, "rb") as f:
                d = tomllib.load(f)
        else:
            continue

        # Load config section, if available
        config_section = d.pop("config", None)
        if isinstance(config_section, dict):
            config.load(config_section)

        # Load the rest into a root CheckBase
        check = CheckBase.load(d, name=str(checks_file))
        checks.append(check)

    return checks


def main_cli():
    # Parse the CLI arguments
    parser = setup_parser()
    args = parser.parse_args()

    # Setup the default logger
    setup_logging(debug=args.debug)
    logger.debug(f"CLI parsed args: {args}")

    # Get the checks
    checks = get_checks(args)

    # Run the checks
    for check in checks:
        check.check()
