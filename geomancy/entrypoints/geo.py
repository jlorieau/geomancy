"""
The 'geo' program entry point.

This file is located in the root module directory, rather than the 'cli'
submodule because it may access functionality from all submodules
"""
import typing as t
import argparse
import logging
from pathlib import Path
from itertools import chain
import tomllib

import yaml

from .. import get_version
from ..config import Config
from ..checks import CheckBase
from ..environment import load_env

__all__ = ("geo_cli",)

__description__ = (
    (Path(__file__).parent / ".." / "__description__.txt").read_text().strip()
)

logger = logging.getLogger(__name__)  # Create a default logger
config = Config()  # Set up config defaults for the CLI

# Set current version
config.VERSION = get_version()

# Default paths for checks files
config.CLI.CHECKS_PATHS = [
    "pyproject.toml",
    ".geomancy.??ml",
    "geomancy.??ml",
    "geomancy.yml",
    ".geomancy.yml",
]

# Default file extensions for TOML files
config.CLI.TOML_EXTS = [".toml"]

# Default file extensions for YAML files
config.CLI.YAML_EXTS = [".yml", ".yaml"]

# Default paths for settings
config.CLI.SETTINGS_PATHS = ["{HOME}/.geomancerrc"]


def filepaths(string: str, required: bool = True) -> t.List[Path]:
    """Given a path string verifies that the path(s) exist converts to path object(s).

    Parameters
    ----------
    string
        The path string to verify and convert, which may include gobs
    required
        If True, log an error and exit the program if the file does not exist

    Returns
    -------
    paths
        The paths for the existing files
    """
    # See if there's a glob pattern in the string
    if any(c in string for c in ("*", "?", "[", "]")):
        # Expand the glob from the current directory
        paths = list(Path(".").glob(string))
    else:
        paths = [Path(string)]

    # Check the paths
    existing_paths = []
    for path in paths:
        if path.is_file():
            existing_paths.append(path)

    if required and len(existing_paths) == 0:
        logger.error(f"Could not find file(s) given by the path '{string}'")
        exit(1)

    return existing_paths


def setup_parser() -> argparse.ArgumentParser:
    """Set up the CLI parser"""
    # Create the parser
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s " + get_version(),
        help="Print the current version",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "-e",
        "--env",
        action="append",
        type=filepaths,
        help="Optional environment file(s) to load",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite environment variables from files",
    )
    parser.add_argument(
        "--disable-color", action="store_true", help="Disable colors in the terminal"
    )
    parser.add_argument(
        "--config-toml", action="store_true", help="Print default config in toml format"
    )
    parser.add_argument(
        "--config-yaml", action="store_true", help="Print default config in yaml format"
    )
    parser.add_argument(
        "checks_files",
        type=filepaths,
        nargs="*",
        help="Optional file containing checks to run",
    )

    return parser


def setup_logging(debug: bool = False):
    """Set up the default logging"""
    logging.basicConfig(
        level=logging.DEBUG if debug else None,
        format="%(levelname)s:%(name)s: %(message)s",
    )


def action_check(args: argparse.Namespace) -> t.Union[bool, None]:
    """Handle execution of the default check mode

    Parameters
    ----------
    args
        The sub-parser arguments

    Returns
    -------
    result
        True if the checks ran successfully
        False if one of the checks failed
        None if no valid checks files were found
    """
    # Retrieve and format the checks files into a single flat list
    if len(args.checks_files) > 0:
        # Use the specified checks_files, if available
        checks_files = args.checks_files
    else:
        # Otherwise use the default paths in the config
        checks_files = [filepaths(p, required=False) for p in config.CLI.CHECKS_PATHS]
        checks_files = [p for p in checks_files if p is not None]

    # At this stage, checks_files is a list of lists of Path objects.
    # It needs to be flattened into a list of Path objects
    checks_files = list(chain(*checks_files))
    logging.debug(f"action_check: checks_files: {checks_files}")

    # Nothing to do if no checks files were found
    if len(checks_files) == 0:
        logger.error(f"Could not find a checks file")
        return None

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

    # Run the checks
    return all(check.check() for check in checks)


def action_env(args, parser) -> int:
    """Hand the environment files (-e) options"""
    # The '--overwrite' flag only makes sense if environment files (-e) are
    # specified
    if args.overwrite and args.env is None:
        parser.error(
            f"The --overwrite flag can only be used when environment files "
            f"(--env) are specified"
        )

    # Retrieve the env_files from the arguments
    env_files = args.env if args.env is not None else []

    # At this stage, env_files is a list of lists of Path objects.
    # It needs to be flattened into a list of Path objects
    env_files = list(chain(*env_files))
    logging.debug(f"action_env: env_values: {env_files}")

    # Load the environment files and keep track of the number of variables
    # substituted
    count = 0
    for filepath in env_files:
        count += load_env(filepath, overwrite=args.overwrite)
    return count


def action_config(args: argparse.Namespace):
    """Handle the output from --config options"""
    if args.config_yaml:
        config.pprint_yaml()
    elif args.config_toml:
        config.pprint_toml()
    else:
        return None
    exit(0)


def geo_cli(args: t.Optional[t.List[str]] = None):
    # Parse the CLI arguments
    parser = setup_parser()
    args = parser.parse_args(args)  # parse root parser args

    # Setup the default logger
    setup_logging(debug=args.debug)
    logger.debug(f"CLI parsed args: {args}")

    # Process the --config flag (will exit if a --config flag is specified)
    action_config(args)

    # Process the --disable-color flag
    if args.disable_color:
        config.TERM.USE_COLOR = False

    # Process the -e/--env files and --overwrite
    action_env(args=args, parser=parser)

    # Process the checks
    result = action_check(args)
    if result is None:
        parser.print_help()
