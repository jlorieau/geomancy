"""The geo CLI entrypoint"""
import logging
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
    cls=DefaultGroup, default="check", default_if_no_args=False, help=description
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
def geo_cli(debug):
    """The main entrypoint for the 'geo' CLI"""
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if debug else None,
        format="%(levelname)s:%(name)s: %(message)s",
    )


# Add sub-commands
geo_cli.add_command(check)
geo_cli.add_command(run)
geo_cli.add_command(config)
