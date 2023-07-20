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

    # If True (default), environment variables in variable_name or
    # variable_value are substituted with the values of other environment
    # variables.
    env_substitute: bool = True

    # The message for checking environment variables
    msg: str = "Check environment variable '{variable_name}'...{status}."

    # Alternative names for the class
    aliases = ('checkEnv',)

    def __init__(self,
                 *args,
                 regex: t.Optional[str] = None,
                 env_substitute: t.Optional[bool] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = regex

        if isinstance(env_substitute, bool):
            self.env_substitute = env_substitute

    @property
    def variable_name(self) -> str:
        """The name of the environment variable with environment variable
        substitution"""
        return (sub_env(self.value) if self.env_substitute else
                self.value)

    @variable_name.setter
    def variable_name(self, value: str) -> None:
        self.value = value

    @property
    def variable_value(self) -> t.Union[None, str]:
        value = os.environ.get(self.variable_name, None)
        if value is not None and self.env_substitute:
            return sub_env(value)
        else:
            return value

    def check(self) -> bool:
        """Check the environment variable value."""
        # Substitute environment variables, if needed
        variable_name = self.variable_name
        variable_value = self.variable_value

        # Make sure the environment variable exists.
        if variable_value is None:
            msg = self.msg.format(variable_name=variable_name,
                                  status='missing')
            p_fail(msg)
            return False

        # Check that the variable has a non-zero value
        if variable_value == '':
            msg = self.msg.format(variable_name=variable_name,
                                  status='empty string')
            p_fail(msg)
            return False

        # Check the regex, if specified
        if (isinstance(self.regex, str) and
            re.match(self.regex, variable_value) is None):
            status = ("value does not match regex "
                      "'{regex}'".format(regex=self.regex))
            msg = self.msg.format(variable_name=variable_name, status=status)
            p_fail(msg)
            return False

        # All checks passed!
        msg = self.msg.format(variable_name=variable_name, status='passed')
        p_pass(msg)
        return True
