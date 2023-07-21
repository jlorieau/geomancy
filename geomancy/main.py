"""
The program entry point.

This file is located in the root module directory, rather than the 'cli'
submodule because it may access functionality from all submodules
"""
import argparse

from . import get_version, __description__


def main_cli():
    # Set up the parser
    parser = argparse.ArgumentParser(description=__description__)

    # Load a custom file with checks
    parser.add_argument(
        "checks_file",
        type=open,
        nargs="?",
        help="Optional file containing checks to run",
    )

    # Enable color terminal
    parser.add_argument(
        "--disable-color", action="store_false", help="Disable colors in the terminal"
    )

    # Print the current version
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s " + get_version()
    )

    # Parse the arguments
    args = parser.parse_args()
