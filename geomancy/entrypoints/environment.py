"""
Options and settings for environment files
"""
import typing as t
import logging

import click

from .utils import filepaths
from ..environment import load_env

__all__ = ("env_options",)

logger = logging.getLogger(__name__)


class RequiredOther(click.Option):
    """Make the use of option require the specification/presence of another
    option"""

    def __init__(self, *args, **kwargs):
        requires = kwargs.pop("requires")
        self.requires = [requires] if isinstance(requires, str) else requires

        assert self.requires, "'requires' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + f" NOTE: This argument requires '{', '.join(self.requires)}' "
            f"options to be specified."
        ).strip()
        super().__init__(*args, **kwargs)

    def handle_parse_result(
        self, ctx: click.Context, opts: t.Mapping[str, t.Any], args: t.List[str]
    ) -> t.Tuple[t.Any, t.List[str]]:
        """Check to make sure that all other required options are specified if this
        option is specified."""
        # If this option is specified, check that the 'requires' field is
        # specified too
        if self.name in opts and not all(req in opts for req in self.requires):
            # Find the missing required parameters
            missing = [req for req in self.requires if req not in opts]

            # Raise an exception
            raise click.BadOptionUsage(
                self.name,
                f"The '{self.name}' option requires the following option(s): "
                f"{', '.join(missing)}",
                ctx=ctx,
            )

        return super().handle_parse_result(ctx, opts, args)


class EnvOption(click.Option):
    """Generate an environment variable dict from environment files"""

    # Whether to overwrite new values over existing values in the environment
    # (i.e. os.environ dict).
    overwrite = False

    def handle_parse_result(
        self, ctx: click.Context, opts: t.Mapping[str, t.Any], args: t.List[str]
    ) -> t.Tuple[t.Any, t.List[str]]:
        """Set the overwrite attribute if the --overwrite flag was set"""
        # Get options
        if "overwrite" in opts:
            self.overwrite = opts["overwrite"]
            logger.debug(f"Environment overwrite set to: {self.overwrite}")

        # Return as normal
        return super().handle_parse_result(ctx, opts, args)

    def process_value(self, ctx: click.Context, value: t.Any) -> t.Any:
        """Process the environment files (-e) option strings into an env dict.

        Returns
        -------
        env
            The processed env dict
        """
        # Set a default, if it's not specified
        value = tuple() if value is None else value

        # Retrieve the env_files from the arguments
        existing_paths = []
        for path in value:
            existing_paths += filepaths(path)

        # Load the environment files and keep track of the number of variables
        # substituted
        env = dict()
        for filepath in existing_paths:
            returned_dict = load_env(filepath, overwrite=self.overwrite)
            env.update(returned_dict)
        return env


# An option group that returns an env dict
def env_options(func=None):
    """Options for loading and using environment files"""
    opts = [
        click.option(
            "--overwrite",
            is_flag=True,
            help="Overwrite environment variables from environment file values",
            cls=RequiredOther,  # Requires the -e/--env options to be set
            requires="env",
            expose_value=False,  # Do not pass to inner command functions
        ),
        click.option(
            "--env",
            "-e",
            multiple=True,
            type=click.Path(exists=True),
            cls=EnvOption,
            help="Environment files to load",
        ),
    ]

    def wrap(inner_func):
        for opt in opts:
            inner_func = opt(inner_func)
        return inner_func

    wrap.__doc__ = env_options.__doc__

    return wrap if func is None else wrap(func)
