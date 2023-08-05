"""Check AWS `S3 buckets`_ and `security settings`_.

- Existence and accessibility
- Public access is disabled

.. _S3 buckets: https://aws.amazon.com/s3/
.. _security settings: https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html
"""
import typing as t
import logging

from .base import CheckAws
from ..base import Result, Executor, CheckException
from ..utils import pop_first
from ...config import Parameter

logger = logging.getLogger(__name__)


class CheckAwsS3BucketAccess(CheckAws):
    """Check AWS S3 bucket availability"""

    msg = Parameter(
        "CHECK_AWS_S3_BUCKET_ACCESS.MSG",
        default="Check AWS S3 bucket access '{check.value}'...",
    )

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        """Check the availability and access to S3 Bucket"""
        msg = self.msg.format(check=self)

        # Get the needed modules, bucket name and boto3 client
        exceptions = self.import_modules("botocore.exceptions")
        bucket_name = self.value.strip()

        # Retrieve the client
        try:
            s3 = self.client("s3")
        except CheckException as exc:
            return Result(status=exc.args[0], msg=msg)

        # Retrieve information on the bucket
        try:
            response = s3.head_bucket(Bucket=bucket_name)
        except exceptions.NoCredentialsError as e:
            # Unable to authenticate the client
            return Result(status="failed (unable to locate credentials)", msg=msg)
        except exceptions.ClientError as e:
            response = e.response

            # Retrieve error information from the response
            error = response["Error"] if "Error" in response else None
            error_code = error["Code"] if error and "Code" in error else ""
            error_msg = error["Message"] if error and "Message" in error else ""

            logger.debug(f"s3.head_bucket error: {error}")

            if error_msg in ("Not Found",) and error_code == "404":
                # Couldn't find the bucket
                return Result(status="failed (not found)", msg=msg)
            elif error_msg in ("Forbidden",) and error_code == "403":
                # Do no have access to an existing bucket
                return Result(status="failed (access forbidden)", msg=msg)
            else:
                return Result(status="failed (unknown reason)", msg=msg)

        except exceptions.ParamValidationError as e:
            # The bucket name failed validation
            report = e.kwargs["report"] if "report" in e.kwargs else None

            if isinstance(report, str):
                return Result(
                    status=f"failed (invalid bucket name '{self.value}')", msg=msg
                )

        # Parse the response
        metadata = (
            response["ResponseMetadata"] if "ResponseMetadata" in response else None
        )
        return_code = (
            metadata["HTTPStatusCode"]
            if metadata and "HTTPStatusCode" in metadata
            else None
        )

        if return_code == 200:
            # Successfully probed S3 bucket
            return Result(status="passed", msg=msg)
        else:
            # It failed, and I don't know why
            return Result(status="failed (unknown reason)", msg=msg)


class CheckAwsS3BucketPrivate(CheckAws):
    """Check AWS S3 buck availability"""

    msg = Parameter(
        "CHECK_AWS_S3_BUCKET_PRIVATE.MSG",
        default="Check AWS S3 bucket private '{check.value}'...",
    )

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        """Check the availability and access to S3 Bucket.

        See: https://stackoverflow.com/a/59002759/9099988
        """
        msg = self.msg.format(check=self)

        # Get the needed modules, bucket name and boto3 client
        exceptions = self.import_modules("botocore.exceptions")
        bucket_name = self.value.strip()

        # Retrieve the client
        try:
            s3 = self.client("s3")
        except CheckException as exc:
            return Result(status=exc.args[0], msg=msg)

        # 1. Check the PublicAccessBlock
        try:
            response = s3.get_public_access_block(Bucket=bucket_name)
        except (exceptions.BotoCoreError, exceptions.ClientError):
            return Result(status="failed (couldn't get public access block)", msg=msg)

        section = response.get("PublicAccessBlockConfiguration", {})
        block_public_policy = section.get("BlockPublicPolicy")
        block_public_acls = section.get("BlockPublicAcls")

        if block_public_policy and block_public_acls:
            return Result(status="passed", msg=msg)

        logger.debug(f"Bucket '{bucket_name}' does not block all public access")

        # 2. Check the Bucket policy to see if it allows public access
        try:
            response = s3.get_bucket_policy_status(Bucket=bucket_name)
        except exceptions.ClientError:
            # No policy found
            response = {}

        # See if a policy was set and whether it allows public access
        section = response.get("PolicyStatus", {})
        public_policy = section.get("IsPublic", False)

        logger.debug(f"Bucket '{bucket_name}' public policy is: {public_policy}")

        # 3. Check the Bucket ACL to see if it allows public access
        try:
            response = s3.get_bucket_acl(Bucket=bucket_name)
        except exceptions.ClientError:
            # No policy found
            response = {}

        # See if ACL grants access
        section = response.get("Grants", {})
        grantee_types = [item.get("Grantee", {}).get("Type", "") for item in section]
        public_acl = any(grantee_type == "Group" for grantee_type in grantee_types)

        logger.debug(f"Bucket '{bucket_name}' ACL to groups is: {public_acl}")

        # Summary
        # If the policy is false and the acl doesn't have a grantee type of 'group',
        # then it should be private
        if not public_policy and not public_acl:
            return Result(status="passed", msg=msg)

        # At this stage, all the checks for private have failed, and it appears
        # that the s3 bucket is publicly accessible
        return Result(status="failed (publicly accessible)", msg=msg)


class CheckAwsS3(CheckAws):
    """Check AWS the availability and permissions of S3 buckets.

    Notes
    -----
    The child checks are meant to verify the accessibility of the bucket as well
    as optionally test for the best security practices`. Current, these include:

    - Default private access (CheckAwsS3BucketPrivate)

    See: https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html
    """

    #: Check that a bucket is private and fail if it is publicly accessible
    private: bool = True

    #: Alternative parameter names for private
    private_aliases = ("private",)

    msg = Parameter(
        "CHECK_AWS_S3.MSG",
        default="Check AWS S3 bucket '{check.value}'",
    )

    aliases = ("checkAWSS3", "CheckAWSS3", "checkS3", "CheckS3")

    def __init__(self, *args, **kwargs):
        # Set up keyword arguments
        self.private = pop_first(kwargs, *self.private_aliases, default=self.private)

        # Set up the rest of the class
        super().__init__(*args, **kwargs)

        # Replace children with bucket sub-checls
        self.children.clear()

        # Bucket accessibility check
        child = CheckAwsS3BucketAccess(*args, **kwargs)
        child.name = f"{self.name}Access"
        self.children.append(child)

        # Bucket public access
        if self.private:
            child = CheckAwsS3BucketPrivate(*args, **kwargs)
            child.name = f"{self.name}Private"
            self.children.append(child)
