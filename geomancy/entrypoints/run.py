"""
The 'run' subcommand
"""
import subprocess
import logging

import click

from .environment import env_options

__all__ = ("run_cmd",)

logger = logging.getLogger(__name__)


@click.command(name="run", context_settings={"ignore_unknown_options": True})
@env_options
@click.argument("args", nargs=-1)
def run_cmd(args, env):
    """Run command within environment"""
    logger.debug(f"args={args}, env={env}")

    # Run the command
    result = subprocess.run(args, env=env)
    return result.returncode
