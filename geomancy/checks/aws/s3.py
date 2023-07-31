"""Checks for AWS resources"""
import typing as t
import logging

from ..base import CheckBase, CheckResult
from ..utils import pop_first
from ...config import Parameter

__all__ = ("CheckAWSS3",)

logger = logging.getLogger(__name__)


class CheckAWSS3(CheckBase):
    """Check AWS the availability and permissions of S3 buckets"""

    # Whether the S3 bucket should be private
    private: bool = True

    # Alternative parameter names for private
    private_aliases = ("private",)

    # The message for checking python packages
    msg = Parameter(
        "CHECKAWSS3.MSG",
        default="Check AWS S3 bucket '{check.value}'...",
    )

    # Other names for this check
    aliases = ("checkAWSS3", "checkAwsS3", "CheckAwsS3")

    # The ImportError message to display if aws modules cannot be loaded
    import_error_msg = (
        "The 'aws' dependency is not installed: {exception}. "
        f"Please reinstall with the '[aws]' or '[all]' extra install "
        f'`python -m pip install "geomancy[aws]"` or '
        f'`python -m pip install "geomancy[all]"`'
    )

    def __init__(self, **kwargs):
        self.private = pop_first(kwargs, *self.private_aliases, default=self.private)
        super().__init__(**kwargs)

    # def is_private(self):
    #     """Determine if the bucket is private"""
    #     # Get the needed modules
    #     boto3, exceptions = self.get_modules("boto3", "botocore.exceptions")
    #
    #     # Get the bucket name from the check value
    #     bucket_name = self.value.strip()

    # NOTE: Move to its own subcheck of CheckAwsS3
    def check_bucket(self, level: int = 0) -> CheckResult:
        """Check that the bucket exists and is accessible"""

    def check(self, level: int = 0) -> CheckResult:
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
                passed=False, msg=self.msg, status="Unable to locate credentials"
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
                return CheckResult(passed=False, msg=self.msg, status="not found")
            elif error_msg in ("Forbidden",) and error_code == "403":
                # Do no have access to an existing bucket
                return CheckResult(
                    passed=False, msg=self.msg, status="access forbidden"
                )
            else:
                return CheckResult(passed=False, msg=self.msg, status="unknown reason")

        except exceptions.ParamValidationError as e:
            # The bucket name failed validation
            report = e.kwargs["report"] if "report" in e.kwargs else None

            if isinstance(report, str):
                return CheckResult(passed=False, msg=self.msg, status=report)
            else:
                return CheckResult(
                    passed=False, msg=self.msg, status="invalid bucket name"
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
            return CheckResult(passed=True, msg=self.msg, status="passed")
        else:
            # It failed, and I don't know why
            return CheckResult(passed=False, msg=self.msg, status="unknown reason")
