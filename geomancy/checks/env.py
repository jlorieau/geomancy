"""
Checks for environment variables
"""
import typing as t
import re

from .base import CheckBase, CheckResult
from ..environment import sub_env
from ..config import Parameter


class CheckEnv(CheckBase):
    """Check the current environment variables."""

    # (Optional) regex to match the environment variable value
    regex: t.Optional[t.Tuple[str, ...]] = None

    # The message for checking environment variables
    msg = Parameter(
        "CHECKENV.MSG",
        default="Check environment variable '{check.raw_value}'...",
    )

    # Alternative names for the class
    aliases = ("checkEnv",)

    def __init__(self, *args, regex: t.Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = regex

    def check(self, level: int = 0) -> CheckResult:
        """Check the environment variable value."""
        # Substitute environment variables, if needed
        value = sub_env(self.raw_value) if self.raw_value is not None else None
        passed = False

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
            passed = True

        msg = self.msg.format(check=self, status=status)
        return CheckResult(passed=passed, msg=msg, status=status)
