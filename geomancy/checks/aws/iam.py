"""Check AWS credentials, Identity and Access Management (`IAM`_) and security
best practices.

Security checks include:


.. _IAM: https://aws.amazon.com/iam/
"""
import typing as t

from .base import CheckAWS, import_error_msg
from ..base import Result, Executor
from ...config import Parameter


class CheckAWSIAMAuthentication(CheckAWS):
    """Checks that the AWS profile can be authenticated"""

    msg = Parameter(
        "CheckAWSIAMAuthentication.MSG",
        default="Check AWS IAM authentication...",
    )

    import_error_msg = import_error_msg

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        boto3, exceptions = self.import_modules("boto3", "botocore.exceptions")

        # Get the STS client to get details on the
        try:
            client = self.client("sts")
        except exceptions.ProfileNotFound:
            return Result(status="profile not found", msg=self.msg)

        # Retrieve caller identity
        try:
            response = client.get_caller_identity()
        except exceptions.ClientError:
            return Result(status="could not authenticate with tokens", msg=self.msg)

        if "Arn" not in response:
            return Result(status="could not verify identity with STS", msg=self.msg)

        arn = response["Arn"]
        return Result(status=f"passed. ARN='{arn}'")


# class CheckAWSIAMRootAccess(CheckAWS):
#     """Check whether root access credentials exist"""
