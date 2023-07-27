"""
Options and settings for environment files
"""
import logging

import click

from .utils import filepaths
from ..environment import load_env

__all__ = ("env_options",)

logger = logging.getLogger(__name__)


def env_options(func=None):
    """Options for loading and using environment files"""
    opts = [
        click.option(
            "--env",
            "-e",
            multiple=True,
            type=click.Path(exists=True),
            help="Environment files to load",
        ),
        click.option(
            "--overwrite",
            is_flag=True,
            help="Overwrite environment variables from environment file values",
        ),
    ]

    def wrap(inner_func):
        for opt in opts:
            inner_func = opt(inner_func)
        return inner_func

    return wrap if func is None else wrap(func)


def handle_env(env, overwrite) -> int:
    """Handle the environment files (-e) options"""
    logger.debug(f"env={env}, overwrite={overwrite}")

    # The '--overwrite' flag only makes sense if environment files (-e) are
    # specified
    if overwrite and len(env) == 0:
        raise click.BadOptionUsage(
            "--overwrite",
            "Can only be used when environment files (--env) are specified",
        )

    # Retrieve the env_files from the arguments
    existing_paths = []
    for path in env:
        existing_paths += filepaths(path)

    # Load the environment files and keep track of the number of variables
    # substituted
    count = 0
    for filepath in existing_paths:
        count += load_env(filepath, overwrite=overwrite)
    return count
