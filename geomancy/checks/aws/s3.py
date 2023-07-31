"""Checks for AWS resources"""
import typing as t
import logging

from ..base import CheckBase, CheckResult
from ..utils import pop_first
from ...config import Parameter

__all__ = ("CheckAWSS3",)

logger = logging.getLogger(__name__)

# The error message to show when AWS modules can't be imported
import_error_msg = (
    "The 'aws' dependency is not installed: {exception}. "
    "Please reinstall with the '[aws]' or '[all]' extra install "
    '`python -m pip install "geomancy[aws]"` or '
    '`python -m pip install "geomancy[all]"`'
)


class CheckAWSS3BucketAccess(CheckBase):
    """Check AWS S3 bucket availability"""

    # The message for checking AWS S3 bucket access
    msg = Parameter(
        "CHECKAWSS3BUCKETACCESS.MSG",
        default="Check AWS S3 bucket access '{check.value}'...",
    )

    # The ImportError message to display if aws modules cannot be loaded
    import_error_msg = import_error_msg

    def check(self, level: int = 0) -> CheckResult:
        """Check the availability and access to S3 Bucket"""
        msg = self.msg.format(check=self)

        # Get the needed modules, bucket name and boto3 client
        boto3, exceptions = self.import_modules("boto3", "botocore.exceptions")
        bucket_name = self.value.strip()
        s3 = boto3.client("s3")

        # Retrieve information on the bucket
        try:
            response = s3.head_bucket(Bucket=bucket_name)

        except exceptions.NoCredentialsError as e:
            # Unable to authenticate the client
            return CheckResult(
                passed=False, msg=msg, status="Unable to locate credentials"
            )

        except exceptions.ClientError as e:
            response = e.response

            # Retrieve error information from the response
            error = response["Error"] if "Error" in response else None
            error_code = error["Code"] if error and "Code" in error else ""
            error_msg = error["Message"] if error and "Message" in error else ""

            logger.debug(f"s3.head_bucket error: {error}")

            if error_msg in ("Not Found",) and error_code == "404":
                # Couldn't find the bucket
                return CheckResult(passed=False, msg=msg, status="not found")
            elif error_msg in ("Forbidden",) and error_code == "403":
                # Do no have access to an existing bucket
                return CheckResult(passed=False, msg=msg, status="access forbidden")
            else:
                return CheckResult(passed=False, msg=msg, status="unknown reason")

        except exceptions.ParamValidationError as e:
            # The bucket name failed validation
            report = e.kwargs["report"] if "report" in e.kwargs else None

            if isinstance(report, str):
                return CheckResult(passed=False, msg=msg, status=report)
            else:
                return CheckResult(passed=False, msg=msg, status="invalid bucket name")

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
            return CheckResult(passed=True, msg=msg, status="passed")
        else:
            # It failed, and I don't know why
            return CheckResult(passed=False, msg=msg, status="unknown reason")


class CheckAWSS3BucketPrivate(CheckBase):
    """Check AWS S3 buck availability"""

    # The message for checking AWS S3 bucket access
    msg = Parameter(
        "CHECKAWSS3BUCKETPRIVATE.MSG",
        default="Check AWS S3 bucket with only private access '{check.value}'...",
    )

    # The ImportError message to display if aws modules cannot be loaded
    import_error_msg = import_error_msg

    def check(self, level: int = 0) -> CheckResult:
        """Check the availability and access to S3 Bucket.

        See: https://stackoverflow.com/a/59002759/9099988
        """
        msg = self.msg.format(check=self)

        # Get the needed modules, bucket name and boto3 client
        boto3, exceptions = self.import_modules("boto3", "botocore.exceptions")
        bucket_name = self.value.strip()
        s3 = boto3.client("s3")

        # 1. Check the PublicAccessBlock
        try:
            response = s3.get_public_access_block(Bucket=bucket_name)
        except (exceptions.BotoCoreError, exceptions.ClientError):
            return CheckResult(
                passed=False, msg=msg, status="Couldn't access PublicAccessBlock"
            )

        section = response.get("PublicAccessBlockConfiguration", {})
        block_public_policy = section.get("BlockPublicPolicy")
        block_public_acls = section.get("BlockPublicAcls")

        if block_public_policy and block_public_acls:
            return CheckResult(passed=True, msg=msg, status="passed")

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
            return CheckResult(passed=True, msg=msg, status="passed")

        # At this stage, all the checks for private have failed, and it appears
        # that the s3 bucket is publicly accessible
        return CheckResult(passed=False, msg=msg, status="publicly accessible")


class CheckAWSS3(CheckBase):
    """Check AWS the availability and permissions of S3 buckets.

    Notes
    -----
    The child checks are meant to verify the accessibility of the bucket as well
    as optionally test for the best security practices`. Current, these include:
        - Default private access (CheckAWSS3BucketPrivate)

    See: https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html
    """

    # Whether to check that the bucket is private
    private: bool = True

    # Alternative parameter names for private
    private_aliases = ("private",)

    # The message for checking AWS Buckets
    msg = Parameter(
        "CHECKAWSS3.MSG",
        default="Check AWS S3 bucket '{check.value}'...",
    )

    # Other names for this check
    aliases = ("checkAWSS3", "checkAwsS3", "CheckAwsS3", "checkS3", "CheckS3")

    def __init__(self, **kwargs):
        # Set up keyword arguments
        self.private = pop_first(kwargs, *self.private_aliases, default=self.private)

        # Set up the rest of the class
        super().__init__(**kwargs)

        # Replace children with bucket sub-checls
        self.children.clear()

        # Bucket accessibility check
        self.children.append(
            CheckAWSS3BucketAccess(name=f"{self.name}Access", value=self.value)
        )

        # Bucket public access
        if self.private:
            self.children.append(
                CheckAWSS3BucketPrivate(name=f"{self.name}Private", value=self.value)
            )
