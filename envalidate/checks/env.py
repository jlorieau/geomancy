"""
Checks environment variables
"""
import typing as t
import os
import re

from .base import CheckBase
from .utils import sub_env
from ..cli import p_pass, p_fail


class CheckEnv(CheckBase):
    """Check the current environment variables"""

    # The name of the environment variable
    variable_name: str

    # (Optional) regex to match the environment variable value
    regex: t.Optional[t.Tuple[str, ...]] = None

    # The message for checking environment variables
    msg = "Check environment variable '{variable_name}'...{status}."

    def __init__(self,
                 *args,
                 variable_name: str,
                 regex: t.Optional[str] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.variable_name = variable_name
        self.regex = regex

    def check(self) -> bool:
        """Check the environment variable value."""
        # Substitute environment variables, if needed
        variable_name = sub_env(self.variable_name)

        # Make sure the environment variable exists.
        if variable_name not in os.environ:
            msg = self.msg.format(variable_name=variable_name,
                                  status='missing')
            p_fail(msg)
            return False

        # Check that the variable has a non-zero value
        value = os.environ[variable_name]
        if value == '':
            msg = self.msg.format(variable_name=variable_name,
                                  status='empty string')
            p_fail(msg)
            return False

        # Check the regex, if specified
        if (isinstance(self.regex, str) and
            re.match(self.regex, value) is None):
            status = ("value does not match regex "
                      "'{regex}'".format(regex=self.regex))
            msg = self.msg.format(variable_name=variable_name, status=status)
            p_fail(msg)
            return False

        # All checks passed!
        msg = self.msg.format(variable_name=variable_name, status='passed')
        p_pass(msg)
        return True
