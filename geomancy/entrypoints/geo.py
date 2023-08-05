"""The geo CLI entrypoint"""
import logging, logging.config
import os
from pathlib import Path

import click
from click_default_group import DefaultGroup

from .check import check
from .run import run
from .config import config
from .. import get_version

logger = logging.getLogger(__name__)

description = (Path(__file__).parent / ".." / "__description__.txt").read_text().strip()


def print_version(context, parameter, value):
    """Print the version"""
    if not value or context.resilient_parsing:
        return
    click.echo(get_version())
    context.exit()


@click.group(
    cls=DefaultGroup, default="check", default_if_no_args=True, help=description
)
@click.option("--debug", "-d", is_flag=True, help="Enable debugging information")
@click.option(
    "--version",
    "-V",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=print_version,
    help="Show the version and exit.",
)
@click.option("--disable-color", is_flag=True, help="Disable terminal coloring")
@click.pass_context
def geo_cli(ctx, debug, disable_color):
    """The main entrypoint for the 'geo' CLI"""
    # Disable coloring, if specified
    if disable_color:
        os.environ["NO_COLOR"] = "TRUE"

    # Setup logging
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "standard": {"format": "%(levelname)s:%(name)s: %(message)s"},
            },
            "handlers": {
                "default": {
                    "level": "DEBUG" if debug else "WARNING",
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",  # Default is stderr
                },
            },
            "loggers": {
                "": {  # root logger
                    "handlers": ["default"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "geomancy": {  # geomancy logs
                    "handlers": ["default"],
                    "level": "DEBUG" if debug else "INFO",
                    "propagate": False,
                },
            },
        }
    )


# Add sub-commands
geo_cli.add_command(check)
geo_cli.add_command(run)
geo_cli.add_command(config)
