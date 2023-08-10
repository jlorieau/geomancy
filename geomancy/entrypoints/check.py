"""
The 'check' subcommand
"""
import typing as t
import logging
import tomllib
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack

import click
import yaml
from rich.live import Live
from rich.console import Group
from rich.rule import Rule
from rich.console import Console, Theme
import rich.progress as progress
from thatway import config, Setting

from .environment import env_options
from .utils import filepaths
from ..checks import Check

__all__ = ("check_cmd",)

# Setup logger and configuration
logger = logging.getLogger(__name__)


# Exception classes
class MissingChecks(click.ClickException):
    """No checks were found in the checks files"""


#: Default paths for checks files
config.cli.checks_paths = Setting(
    (
        "pyproject.toml",
        ".geomancy.??ml",
        "geomancy.??ml",
        "geomancy.yml",
        ".geomancy.yml",
    )
)

#: Default file extensions for TOML files
config.cli.toml_exts = Setting((".toml",))

#: Default file extensions for YAML files
config.cli.yaml_exts = Setting((".yml", ".yaml"))

#: Names for the config section in checks files
config.cli.config_sections = Setting(("config", "Config"))


def validate_checks_files(
    ctx: click.Context, param: click.Parameter, values: t.Tuple[str]
):
    """Validate the checks files arguments and convert to valid paths"""
    # Convert filepath strings into Path objects. Use default locations if
    # no checks_files were specified (i.e. it is an empty list)
    existing_files = []
    for path in values or config.cli.checks_paths:
        existing_files += filepaths(path)

    # Nothing to do if no checks files were found
    if len(existing_files) == 0:
        raise click.MissingParameter(
            "Could not find a checks file.", ctx=ctx, param=param
        )
    logging.debug(f"Checking the following files: {existing_files}")
    return existing_files


# Setup 'check' command
@click.command(name="check")
@env_options
@click.argument("checks_files", nargs=-1, type=str, callback=validate_checks_files)
def check_cmd(checks_files, env):
    """Run checks"""
    logger.debug(f"check_files={checks_files}, env={env}")

    # Convert the checks_files into checks
    checks = []
    for checks_file in checks_files:
        # Parse the file by filetype
        if checks_file.suffix in config.cli.toml_exts:
            with open(checks_file, "rb") as f:
                d = tomllib.load(f)

        elif checks_file.suffix in config.cli.yaml_exts:
            with open(checks_file, "r") as f:
                d = yaml.load(f, Loader=yaml.SafeLoader)

        else:
            continue

        # pyproject.toml files have their items placed under the [tool.geomancy]
        # section
        if checks_file.name == "pyproject.toml":
            d = d.get("tool", dict()).get("geomancy", dict())

        # Load config section, if available
        for config_name in config.cli.config_sections:
            config_section = d.pop(config_name, None)
            if isinstance(config_section, dict):
                config.update(config_section)

        # Load the rest into a root CheckBase
        check = Check.load(d, name=str(checks_file))
        if check is not None:
            checks.append(check)

    # Create a root check, if there are a lot of checks
    if len(checks) > 1:
        check = Check(name=f"Checking {len(checks)} files", children=checks)
    elif len(checks) == 1:
        check = checks[0]
    else:
        plural = True if len(checks_files) > 1 else False
        raise MissingChecks(
            f"No checks were found in the file{'s' if plural else ''}: "
            f"{', '.join(map(str, checks_files))}."
        )

    # Set up a console for rendering to the terminal
    console = Console(theme=Theme({"repr.number": ""}))

    with ExitStack() as stack:
        # Context manager for running checks in multiple threads
        executor = stack.enter_context(ThreadPoolExecutor())

        # Context manager for rendering live to the terminal (rich)
        live = stack.enter_context(Live(refresh_per_second=4, console=console))

        # Run the checks, display the results to the terminal
        result = check.check(executor=executor)

        # Get the total number of checks
        check_total = len(check.flatten)

        # Set up a progress bar and render group
        pbar = progress.Progress(
            progress.SpinnerColumn(),
            progress.BarColumn(),
            progress.TextColumn("checks"),
            progress.MofNCompleteColumn(),
            progress.TimeRemainingColumn(),
        )
        task1 = pbar.add_task("checking...", total=check_total)

        # Update the display until the checks are done
        while not result.done:
            time.sleep(0.5)

            # Update progress
            pbar.update(task1, completed=len(result.finished))

            # Update group
            group = Group(
                result.rich_table(),
                pbar.make_tasks_table(tasks=pbar.tasks),
            )
            live.update(group)

        # Create a summary line to render
        passed_total = len([r for r in result.finished if r.passed])
        failed_total = check_total - passed_total
        elapsed = sum(task.elapsed for task in pbar.tasks if task.elapsed is not None)

        if result.passed:
            color = "green"
            title = f"[{color}][bold]{passed_total} passed[/bold][/{color}]"
        else:
            color = "red"
            title = f"[{color}][bold]{failed_total} failed[/bold][/{color}]"

        title = f"{title}[{color}] in {elapsed:.2f}s[/{color}]"
        status = Rule(title=title, characters="=", style=color)

        # Print the final table and summary
        group = Group(result.rich_table(), status)
        live.update(group)

    if not result.passed:
        exit(1)

    return result.passed
