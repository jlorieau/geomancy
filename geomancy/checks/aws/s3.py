"""Checks for AWS resources"""
import typing as t
import logging

from ..base import CheckBase, CheckResult
from ..utils import pop_first
from ...config import Parameter

__all__ = ("CheckAWSS3",)

logger = logging.getLogger(__name__)


class CheckAWSS3BucketAccess(CheckBase):
    """Check AWS S3 buck availability"""

    # The message for checking AWS S3 bucket access
    msg = Parameter(
        "CHECKAWSS3BUCKETACCESS.MSG",
        default="Check AWS S3 bucket access '{check.value}'...",
    )

    # The ImportError message to display if aws modules cannot be loaded
    import_error_msg = (
        "The 'aws' dependency is not installed: {exception}. "
        f"Please reinstall with the '[aws]' or '[all]' extra install "
        f'`python -m pip install "geomancy[aws]"` or '
        f'`python -m pip install "geomancy[all]"`'
    )

    def check(self, level: int = 0) -> CheckResult:
        """Check the availability and access to S3 Bucket"""
        msg = self.msg.format(check=self)

        # Get the needed modules
        boto3, exceptions = self.import_modules("boto3", "botocore.exceptions")

        # Get the bucket name from the check value
        bucket_name = self.value.strip()

        # Get access to the AWS SDK
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


class CheckAWSS3(CheckBase):
    """Check AWS the availability and permissions of S3 buckets"""

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
    aliases = ("checkAWSS3", "checkAwsS3", "CheckAwsS3")

    def __init__(self, **kwargs):
        # Set up keyword arguments
        self.private = pop_first(kwargs, *self.private_aliases, default=self.private)

        # Set up the rest of the class
        super().__init__(**kwargs)

        # Replace children with bucket sub-checls
        self.children.clear()
        self.children += [
            CheckAWSS3BucketAccess(name=f"{self.name}Access", value=self.value)
        ]
