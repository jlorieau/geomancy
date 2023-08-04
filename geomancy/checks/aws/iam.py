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

from .base import CheckAws
from ..base import Result, Executor, CheckException
from ..utils import pop_first
from ...config import Parameter

logger = logging.getLogger(__name__)


class CheckAwsIamAuthentication(CheckAws):
    """Checks that the AWS profile can be authenticated"""

    msg = Parameter(
        "CHECK_AWS_IAM_AUTHENTICATION.MSG",
        default="Check AWS IAM authentication",
    )

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        msg = self.msg.format(check=self)
        exceptions = self.import_modules("botocore.exceptions")

        # Get the STS client to get details on the
        try:
            sts = self.client("sts")
        except CheckException as exc:
            return Result(status=exc.args[0], msg=msg)

        # Retrieve caller identity
        try:
            response = sts.get_caller_identity()
        except exceptions.ClientError:
            return Result(
                status="failed (can't authenticate with given tokens)", msg=msg
            )

        if "Arn" not in response:
            return Result(status="failed (can't verify identity with STS)", msg=msg)

        arn = response["Arn"]
        return Result(status=f"passed. ARN='{arn}'")


class CheckAwsIamAccessKeyAge(CheckAws):
    """Check the age of AWS access keys"""

    #: The key age in days
    key_age: int

    #: The default key age (in days)
    key_age_default: int = Parameter("CHECK_AWS_IAM_ACCESS_KEY_AGE.KEY_AGE", default=90)

    #: Aliases for the key_age parameter
    key_age_aliases = ("key_age", "age")

    msg = Parameter(
        "CHECK_AWS_IAM_ACCESS_KEY_AGE.MSG",
        default="Check AWS IAM access key age ({check.key_age} days)",
    )

    def __init__(self, *args, **kwargs):
        # Retrieve kwargs
        self.key_age = pop_first(
            kwargs, *self.key_age_aliases, default=self.key_age_default
        )
        super().__init__(*args, **kwargs)

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        msg = self.msg.format(check=self)
        exceptions = self.import_modules("botocore.exceptions")

        # Get the IAM client and username
        try:
            iam = self.client("iam")
            username = self.username()
        except CheckException as exc:
            return Result(status=exc.args[0], msg=msg)

        # Retrieve the list of access keys for the given username
        try:
            response = iam.list_access_keys(UserName=username)
            access_keys = response["AccessKeyMetadata"]
            access_key_dates = {d["AccessKeyId"]: d["CreateDate"] for d in access_keys}
        except KeyError:
            return Result(status="failed (could not parse list_access_key)")

        # Find which keys are too old
        old_keys = dict()
        for key_id, key_date in access_key_dates.items():
            delta = datetime.datetime.now(tz=None) - key_date.replace(tzinfo=None)

            if delta.days > self.key_age:
                old_keys[key_id] = key_date

        if old_keys:
            # There were keys older than self.ket_age, this is a fail
            return Result(
                status=(
                    f"failed ({' and '.join(old_keys)} are older than "
                    f"{self.key_age} days)"
                ),
                msg=msg,
            )
        else:
            return Result(status="passed", msg=msg)


class CheckAwsIamRootAccess(CheckAws):
    """Check the presence of AWS account (root) access Keys

    see: https://aws.amazon.com/blogs/security/an-easier-way-to-determine-the-presence-of-aws-account-access-keys/ # noqa
    """

    msg = Parameter(
        "CHECK_AWS_IAM_ROOT_ACCESS.MSG",
        default="Check AWS IAM root keys are not present",
    )

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        msg = self.msg.format(check=self)
        exceptions = self.import_modules("botocore.exceptions")

        # Get the IAM client
        try:
            iam = self.client("iam")
        except CheckException as exc:
            return Result(status=exc.args[0], msg=msg)

        # Get the account summary
        try:
            response = iam.get_account_summary()
        except exceptions.ClientError:
            return Result(status="failed (couldn't authenticate host)", msg=msg)

        # See if the expected items are in the response and fail if they aren't
        if (
            "SummaryMap" not in response
            or "AccountAccessKeysPresent" not in response["SummaryMap"]
            or "AccountSigningCertificatesPresent" not in response["SummaryMap"]
        ):
            logger.debug(str(response))
            return Result(status="failed (couldn't retrieve account summary)", msg=msg)

        summary = response["SummaryMap"]
        has_account_access_key = summary["AccountAccessKeysPresent"] != 0
        has_account_signing_certs = summary["AccountSigningCertificatesPresent"] != 0

        # Track statuses that amount to a fail
        statuses = []
        if has_account_access_key:
            statuses.append("account has root access keys")
        if has_account_signing_certs:
            statuses.append("account has signing certificates")

        if statuses:
            return Result(status=f"failed ({' and '.join(statuses)})", msg=msg)
        else:
            return Result(status="passed", msg=msg)


class CheckAwsIam(CheckAws):
    """Check the IAM access credentials and settings"""

    #: Check whether root secret keys or signing certs exist
    root_access: bool

    #: Default value for the root_access parameter
    root_access_default = Parameter("CHECK_AWS_IAM.ROOT_ACCESS", True)

    #: Aliases for the root_access parameter
    root_access_aliases = ("root_access", "root")

    #: Check the key age (in days)
    key_age: t.Optional[int]

    #: Default value for key_age (see :class:`CheckAwsIamAccessKeyAge`)
    key_age_default = Parameter("CHECK_AWS_IAM_ACCESS_KEY_AGE.KEY_AGE")

    #: Aliases for the key_age parameter
    key_age_aliases = ("key_age", "age")

    def __init__(self, *args, **kwargs):
        # Set up keyword arguments
        self.root_access = pop_first(
            kwargs, *self.root_access_aliases, default=self.root_access_default
        )
        self.key_age = pop_first(
            kwargs, *self.key_age_aliases, default=self.key_age_default
        )

        # Set up the rest of the class
        super().__init__(*args, **kwargs)

        # Replace children
        self.children.clear()

        # Add sub-checks
        # 1. CheckAwsIamAuthentication
        check_auth_kwargs = kwargs.copy()
        check_auth_kwargs["name"] = f"{self.name}Authentication"
        check_auth = CheckAwsIamAuthentication(*args, **kwargs)
        self.children.append(check_auth)

        # 2. CheckAwsIamAccessKeyAge
        if isinstance(self.key_age, int):
            check_age_kwargs = kwargs.copy()
            check_age_kwargs["name"] = f"{self.name}AccessKeyAge"
            check_age_kwargs["key_age"] = self.key_age
            check_age = CheckAwsIamAccessKeyAge(*args, **kwargs)
            self.children.append(check_age)

        # 3. CheckAwsIAMRootAccess
        if self.root_access:
            check_root_kwargs = kwargs.copy()
            check_root_kwargs["name"] = f"{self.name}RootAccess"
            check_root = CheckAwsIamRootAccess(*args, **kwargs)
            self.children.append(check_root)
