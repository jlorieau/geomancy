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


class CheckAWSIAMRootAccess(CheckAWS):
    """Check the presence of AWS account (root) access Keys

    see: https://aws.amazon.com/blogs/security/an-easier-way-to-determine-the-presence-of-aws-account-access-keys/ # noqa
    """

    msg = Parameter(
        "CHECKAWSIAMROOTACCESS.MSG", default="Check AWS IAM root keys are not present"
    )

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        boto3, exceptions = self.import_modules("boto3", "botocore.exceptions")

        # Get the IAM client
        try:
            iam = self.client("iam")
            response = iam.get_account_summary()
        except (exceptions.ProfileNotFound, exceptions.ClientError):
            return Result(status="failed to authenticate host", msg=self.msg)

        # See if the expected items are in the response and fail if they aren't
        if (
            "SummaryMap" not in response
            or "AccountAccessKeysPresent" not in response["SummaryMap"]
            or "AccountSigningCertificatesPresent" not in response["SummaryMap"]
        ):
            logger.debug(str(response))
            return Result(status="failed to retrieve account summary")

        summary = response["SummaryMap"]
        has_account_access_key = summary["AccountAccessKeysPresent"] != 0
        has_account_signing_certs = summary["AccountSigningCertificatesPresent"] != 0
        print(summary)
        # Track statuses that amount to a fail
        statuses = []
        if has_account_access_key:
            statuses.append("account has root access keys")
        if has_account_signing_certs:
            statuses.append("account has signing certificates")

        if statuses:
            return Result(status=f"failed ({' and '.join(statuses)})", msg=self.msg)
        else:
            return Result(status="passed", msg=self.msg)


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
