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


def setup_parsers() -> t.Dict[str, argparse.ArgumentParser]:
    """Set up the CLI parsers"""
    # Create the parser
    parser = argparse.ArgumentParser(description=__description__)
    subparsers = parser.add_subparsers(dest="subparser")

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

    # Check subparser
    check_parser = subparsers.add_parser("check", help="Run checks (default)")

    check_parser.add_argument(
        "checks_files",
        type=filepath,
        nargs="*",
        help="Optional file containing checks to run",
    )

    # Config subparser
    config_parser = subparsers.add_parser(
        "config", help="View and manage configuration"
    )
    return {
        "parser": parser,
        "check_parser": check_parser,
        "config_parser": config_parser,
    }


def setup_logging(debug: bool = False):
    """Set up the default logging"""
    logging.basicConfig(
        level=logging.DEBUG if debug else None,
        format="%(name)s:%(levelname)s: %(message)s",
    )


def action_check(args: argparse.Namespace) -> bool:
    """Handle execution of the 'check' sub-command

    Parameters
    ----------
    args
        The sub-parser arguments

    Returns
    -------
    successful
        True if the command ran successfully
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
    if len(checks_files) == 0:
        logger.error(f"Could not find a checks file")
        return False

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

    # Run the checks
    for check in checks:
        check.check()

    return True  # The action was completed successfully--regardless of the checks


def action_config(args):
    """Handle execution of the 'config' sub-command"""


def main_cli():
    # Parse the CLI arguments
    parsers = setup_parsers()
    parser = parsers["parser"]  # root parser
    args, extra = parser.parse_known_args()  # parse root parser args

    # Setup the default logger
    setup_logging(debug=args.debug)
    logger.debug(f"CLI parsed args: {args}")

    # Find the sub-command and continue parser
    if args.subparser == "check" or args.subparser is None:
        check_parser = parsers["check_parser"]
        args = check_parser.parse_args(extra)
        successful = action_check(args)
        if not successful:
            check_parser.print_help()
    elif args.subparser == "config":
        config_parser = parsers["config_parser"]
        args = config_parser.parse_args(extra)
        action_config(args)
    else:
        raise NotImplementedError(f"Unknown subcommand {args.subparser}")
