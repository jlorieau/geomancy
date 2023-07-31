"""Tests for AWS checks"""
import pytest


from geomancy.checks.aws import CheckAWSS3


@pytest.mark.vcr
def test_check_aws_s3_missing():
    """Test CheckAWSS3 check with a missing bucket"""
    bucket_name = "my-missing-bucket-noexist"

    check = CheckAWSS3(name="Missing Bucket", value=bucket_name)
    result = check.check()
    assert not result.passed
    assert result.status == "not found"


@pytest.mark.vcr
def test_check_aws_s3_forbidden():
    """Test CheckAWSS3 check with a bucket that has forbidden access"""
    bucket_name = "docker"

    check = CheckAWSS3(name="Forbidden Bucket", value=bucket_name)
    result = check.check()
    assert not result.passed
    assert result.status == "access forbidden"


def test_check_aws_s3_invalid():
    """Test CheckAWSS3 check with a bucket that has an invalid name"""
    bucket_name = "!invalid!"

    check = CheckAWSS3(name="Invalid Bucket", value=bucket_name)
    result = check.check()
    assert not result.passed
    assert result.status.startswith("Invalid bucket name")


@pytest.mark.vcr
def test_check_aws_s3_valid():
    """Test CheckAWSS3 check with a valid bucket"""
    bucket_name = "valid"

    check = CheckAWSS3(name="Valid Bucket", value=bucket_name)
    result = check.check()
    assert result.passed
    assert result.status.startswith("passed")
