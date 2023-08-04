"""Check AWS credentials, Identity and Access Management (`IAM`_) and security
best practices.

Checks include:

- Authentication with the default or specified profile
- Access key age (90 days)


.. _IAM: https://aws.amazon.com/iam/
"""
import typing as t
import logging
import datetime

from .base import CheckAWS
from ..base import Result, Executor
from ...config import Parameter

logger = logging.getLogger(__name__)

__all__ = ("CheckAWSIAMAccessKeyAge",)


class CheckAWSIAMAuthentication(CheckAWS):
    """Checks that the AWS profile can be authenticated"""

    msg = Parameter(
        "CHECKAWSIAMAUTHENTICATION.MSG",
        default="Check AWS IAM authentication",
    )

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        exceptions = self.import_modules("botocore.exceptions")

        # Get the STS client to get details on the
        try:
            sts = self.client("sts")
        except exceptions.ProfileNotFound:
            return Result(status="failed to find profile", msg=self.msg)

        # Retrieve caller identity
        try:
            response = sts.get_caller_identity()
        except exceptions.ClientError:
            return Result(status="failed to authenticate with tokens", msg=self.msg)

        if "Arn" not in response:
            return Result(status="failed verify identity with STS", msg=self.msg)

        arn = response["Arn"]
        return Result(status=f"passed. ARN='{arn}'")


class CheckAWSIAMAccessKeyAge(CheckAWS):
    """Check the age of AWS access keys"""

    #: The key age in days
    key_age: int

    #: The default key age (in days)
    key_age_default: int = Parameter("CHECKAWSIAMACCESSKEYAGE.KEY_AGE", default=90)

    msg = Parameter(
        "CHECKAWSIAMACCESSKEYAGE.MSG",
        default="Check AWS IAM access key age (check.value days)",
    )

    def __init__(self, *args, key_age: t.Optional[int] = None, **kwargs):
        self.key_age = key_age if key_age is not None else self.key_age_default
        super().__init__(*args, **kwargs)

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        msg = self.msg.format(check=self)
        exceptions = self.import_modules("botocore.exceptions")

        # Get the IAM client
        try:
            iam = self.client("iam")
            response = iam.get_user()
        except (exceptions.ProfileNotFound, exceptions.ClientError):
            return Result(status="failed to authenticate host", msg=msg)

        # Get the age of the key
        if "User" not in response or "CreateDate" not in response["User"]:
            logger.debug(str(response))
            return Result(status="failed to get user information", msg=msg)

        # Get the delta in age
        date = response["User"]["CreateDate"]
        delta = datetime.datetime.now(tz=None) - date.replace(tzinfo=None)

        if delta.days > self.key_age:
            return Result(status=f"failed ({delta.days} days)", msg=msg)
        else:
            return Result(status="passed", msg=msg)
