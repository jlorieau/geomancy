"""
Check the existence and, optionally, the value of an environment variable.
"""
import typing as t
import re

from .base import Check, Result, Executor
from ..environment import sub_env
from ..config import Parameter


class CheckEnv(Check):
    """Check the current environment variables."""

    #: (Optional) regex to match the environment variable value
    regex: t.Optional[t.Tuple[str, ...]] = None

    msg = Parameter(
        "CHECKENV.MSG",
        default="Check environment variable '{check.raw_value}'",
    )

    aliases = ("checkEnv",)

    def __init__(self, *args, regex: t.Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = regex

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        """Check the environment variable value."""
        # Substitute environment variables, if needed
        value = sub_env(self.raw_value) if self.raw_value is not None else None

        if value is None:
            # If the value is None, the environment variable doesn't exist.
            status = "missing"
        elif value == "":
            # An empty string environment variable is considered not set
            status = "empty string"
        elif isinstance(self.regex, str) and re.match(self.regex, value) is None:
            # Check the regex, if specified
            status = f"does not match regex '{self.regex}'"
        else:
            # All checks passed!
            status = "passed"

        msg = self.msg.format(check=self, status=status)
        return Result(msg=msg, status=status)
