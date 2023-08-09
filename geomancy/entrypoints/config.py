"""
The 'config' subcommand
"""
import logging

from thatway import config

import click

__all__ = ("config_cmd",)

logger = logging.getLogger(__name__)


@click.command(name="config")
@click.option("--toml", is_flag=True, help="Print default config in toml format")
@click.option("--yaml", is_flag=True, help="Print default config in yaml format")
def config_cmd(toml, yaml, **kwargs):
    """Configuration information"""
    logger.debug(f"toml={toml}, yaml={yaml}")

    if toml:
        print(config.dumps_toml())
    else:
        print(config.dumps_yaml())
