"""
The 'run' subcommand
"""
import logging

import click

from .environment import env_options, handle_env

__all__ = ("run",)

logger = logging.getLogger(__name__)


@click.command
@env_options
def run(**kwargs):
    """Run command within environment"""
    # Hand environment file options
    env_count = handle_env(**kwargs)
