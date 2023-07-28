"""
The 'run' subcommand
"""
import subprocess
import logging

import click

from .environment import env_options, handle_env

__all__ = ("run",)

logger = logging.getLogger(__name__)


@click.command(context_settings={"ignore_unknown_options": True})
@env_options
@click.argument("args", nargs=-1)
def run(args, **kwargs):
    """Run command within environment"""
    logger.debug(f"args={args}")

    # Hand environment file options
    env = handle_env(**kwargs)

    # Run the command
    result = subprocess.run(args, env=env)
    return result.returncode
