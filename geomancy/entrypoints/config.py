"""
The 'config' subcommand
"""
import logging

import click

from ..config import Config

__all__ = ("config",)

logger = logging.getLogger(__name__)


@click.command
@click.option("--toml", is_flag=True, help="Print default config in toml format")
@click.option("--yaml", is_flag=True, help="Print default config in yaml format")
def config(toml, yaml, **kwargs):
    """Configuration information"""
    logger.debug(f"toml={toml}, yaml={yaml}")

    conf = Config()
    if toml:
        conf.pprint_toml()
    else:
        conf.pprint_yaml()
