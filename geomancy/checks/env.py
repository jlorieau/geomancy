"""
Checks for environment variables
"""
import typing as t
import os
import re

from .base import CheckBase
from .utils import sub_env
from ..config import Parameter
from ..cli import term


class CheckEnv(CheckBase):
    """Check the current environment variables.

    Notes
    -----
    This function can substitute variable names and values with other
    environment variables, which is common with environment variables.

    e.g. With the following environment variables:
    ENV=DEV
    DEPLOYMENT_DEV=passed

    The user could use the variable name 'DEPLOYMENT_{ENV}' to match
    'DEPLOYMENT_DEV'.
    """

    value: str

    # (Optional) regex to match the environment variable value
    regex: t.Optional[t.Tuple[str, ...]] = None

    # The message for checking environment variables
    msg: str = Parameter(
        "CHECKENV.MSG",
        default="Check environment variable " "'{name}'...{status}.",
    )

    # Alternative names for the class
    aliases = ("checkEnv",)

    def __init__(
        self,
        *args,
        regex: t.Optional[str] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.regex = regex

    def check(self, level: int = 0) -> bool:
        """Check the environment variable value."""
        # Substitute environment variables, if needed
        name = self.name
        value = self.value

        # Make sure the environment variable exists.
        if value is None:
            msg = self.msg.format(name=name, status="missing")
            term.p_fail(msg, level=level)
            return False

        # Check that the variable has a non-zero value
        if value == "":
            msg = self.msg.format(name=name, status="empty string")
            term.p_fail(msg, level=level)
            return False

        # Check the regex, if specified
        if isinstance(self.regex, str) and re.match(self.regex, value) is None:
            status = "value does not match regex " "'{regex}'".format(regex=self.regex)
            msg = self.msg.format(name=name, status=status)
            term.p_fail(msg, level=level)
            return False

        # All checks passed!
        msg = self.msg.format(name=name, status="passed")
        term.p_pass(msg, level=level)
        return True
