"""Check AWS Systems Manager (`SSM`_) and related `SSM security settings`_.

- Parameter existence and type

.. _SSM: https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html
.. _SSM security settings: https://docs.aws.amazon.com/systems-manager/latest/userguide/security.html
"""

import typing as t
import logging

from thatway import Setting

from .base import CheckAws
from ..base import Result, Executor, CheckException
from ..utils import pop_first

logger = logging.getLogger(__name__)


class CheckAwsSsmParameter(CheckAws):
    """Check AWS SSM parameter availability"""

    #: The parameter type, either 'String', 'StringList', 'SecureString'
    #: If None, the parameter type won't be checked
    type: t.Optional[str]

    #: The default type to check for the parameter type, either
    #: 'String', 'StringList', 'SecureString' or None
    type_default = Setting("String")

    #: The allowed values for the 'type' attribute
    allowed_types = Setting(("String", "StringList", "SecureString"))

    msg = Setting("Check AWS SSM parameter access '{check.value}'")

    aliases = ("checkSsmParameter", "checkSsmParam", "checkAWSSSMParameter")

    #: Class-level cache for parameters lists, sorted by profile username,
    #: then by parameter name
    _cache: t.Dict[str, t.Dict[str, dict]] = {}

    def __init__(self, *args, **kwargs):
        # Set up keyword arguments
        self.type = pop_first(kwargs, "type", default=self.type_default)
        super().__init__(*args, **kwargs)

        # Check the attributes
        if self.type is not None and self.type not in self.allowed_types:
            raise CheckException(
                f"Parameter type '{self.type}' not in {self.allowed_types}"
            )

    def get_parameters(self) -> dict:
        """Retrieve a dict of parameters for the given profile.

        Returns
        -------
        parameters
            The parameter name (key) and parameter values in a dict (values).

        Raises
        ------
        CheckException
            Raised if the client could be retrieved
        """
        # Check the cache by username
        username = self.username()
        if username in self._cache:
            return self._cache[username]

        # Retrieve all available parameters
        ssm = self.client("ssm")

        # Parse the response
        parameters = dict()
        next_token = ""
        while next_token is not None:
            # Retrieve a page of parameters, with the next token for the next page
            # (if available)
            response = ssm.describe_parameters(NextToken=next_token)
            next_token = response.get("NextToken", None)

            # Parse the response
            if "Parameters" in response:
                parameters.update({p["Name"]: p for p in response["Parameters"]})

        # cache the parameters
        return self._cache.setdefault(username, parameters)

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        """Check the availability of the given SSM parameter"""
        msg = self.msg.format(check=self)

        # Get the needed modules, bucket name and boto3 client
        exceptions = self.import_modules("botocore.exceptions")
        parameter_name = self.value.strip()

        # Retrieve the parameters for the current profile
        try:
            parameters = self.get_parameters()
        except CheckException as exc:
            return Result(status=exc.args[0], msg=msg)

        # Retrieve information on the parameter
        if parameter_name not in parameters:
            return Result(status=f"failed (could not find '{parameter_name}')", msg=msg)

        param = parameters[parameter_name]
        param_type = param["Type"]

        # Wrong type
        if self.type is not None and param_type != self.type:
            return Result(
                status=f"failed (parameter '{parameter_name}' has wrong "
                f"type '{param_type}')",
                msg=msg,
            )

        return Result(status="passed", msg=msg)
