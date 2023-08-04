"""Tests for CheckAWSS3"""
import pytest


from geomancy.checks.aws.s3 import (
    CheckAwsS3,
    CheckAwsS3BucketAccess,
    CheckAwsS3BucketPrivate,
)

# Basic accessibility tests


# @pytest.mark.parametrize(
#     "cls", (CheckAwsS3, CheckAwsS3BucketAccess, CheckAwsS3BucketAccess)
# )
# def test_check_aws_profile(cls):
#     """Test that CheckAws profiles are properly loaded"""
#     assert False


@pytest.mark.vcr
def test_check_aws_s3_missing():
    """Test CheckAwsS3/CheckAwsS3BucketAccess check with a missing bucket"""
    bucket_name = "my-missing-bucket-noexist"

    # Run the check, which should not pass
    check = CheckAwsS3(name="Missing Bucket", value=bucket_name)
    result = check.check()
    assert not result.passed

    # Validate the result of the first child check, CheckAwsS3BucketAccess,
    # which could not find the bucket
    child_results = result.children
    assert not child_results[0].passed
    assert child_results[0].status == "failed (not found)"


@pytest.mark.vcr
def test_check_aws_s3_forbidden():
    """Test CheckAwsS3/CheckAwsS3BucketAccess check with a bucket that has
    forbidden access"""
    bucket_name = "docker"

    # Run the check, which should not pass
    check = CheckAwsS3(name="Forbidden Bucket", value=bucket_name)
    result = check.check()
    assert not result.passed

    # Validate the result of the first child check, CheckAwsS3BucketAccess,
    # which found that the bucket access is forbidden
    child_results = result.children
    assert not child_results[0].passed
    assert child_results[0].status == "failed (access forbidden)"


def test_check_aws_s3_invalid():
    """Test CheckAwsS3/CheckAwsS3BucketAccess check with a bucket that has an
    invalid name"""
    bucket_name = "!invalid!"

    # Run the check, which should not pass
    check = CheckAwsS3(name="Invalid Bucket", value=bucket_name)
    result = check.check()
    assert not result.passed

    # Validate the result of the first child check, CheckAwsS3BucketAccess,
    # which found the bucket name to be invalid
    child_results = result.children
    assert not child_results[0].passed
    assert child_results[0].status.startswith("failed (Invalid bucket name")


# The following are public/private bucket tests
@pytest.mark.vcr
def test_check_aws_s3_without_public_access_block():
    """Test CheckAwsS3/CheckAwsS3BucketPrivate check using a bucket with
    Public Access Block turned off."""
    # The following is a bucket created with "Block Public Access" turned off
    # but without a policy or ACL specified. Altogether, it should not give
    # public access
    bucket_name = "testbucket-nopublicblock"

    # Run the check, which should not pass
    check = CheckAwsS3(name="Public Bucket", value=bucket_name)
    result = check.check()
    assert result.passed

    # Validate the result of the second child check, CheckAwsS3BucketAccess,
    # which found the bucket name to be invalid
    child_results = result.children
    assert child_results[1].passed


@pytest.mark.vcr
def test_check_aws_s3_public_policy():
    """Test CheckAwsS3/CheckAwsS3BucketPrivate check using a bucket with a
    public Policy."""
    # The following is a bucket created with "Block Public Access" turned off
    # and with a policy that allows public access. This bucket should be
    # publicly accessible and will fail the test
    bucket_name = "testbucket-public-policy"

    # Run the check, which should not pass
    check = CheckAwsS3(name="Public Bucket", value=bucket_name)
    result = check.check()
    assert not result.passed

    # Validate the result of the second child check, CheckAwsS3BucketAccess,
    # which found the bucket name to be invalid
    child_results = result.children
    assert not child_results[1].passed
    assert child_results[1].status == "failed (publicly accessible)"


@pytest.mark.vcr
def test_check_aws_s3_public_acl():
    """Test CheckAwsS3/CheckAwsS3BucketPrivate check using a bucket with a
    public ACL."""
    # The following is a bucket created with "Block Public Access" turned off
    # and with a policy that allows public access. This bucket should be
    # publicly accessible and will fail the test
    bucket_name = "testbucket-alluser-acl"

    # Run the check, which should not pass
    check = CheckAwsS3(name="Public Bucket", value=bucket_name)
    result = check.check()
    assert not result.passed

    # Validate the result of the second child check, CheckAwsS3BucketAccess,
    # which found the bucket name to be invalid
    child_results = result.children
    assert not child_results[1].passed
    assert child_results[1].status.startswith("failed (publicly accessible)")


@pytest.mark.vcr
def test_check_aws_s3_valid():
    """Test CheckAwsS3 check with a valid bucket"""
    bucket_name = "testbucket-valid"

    # Run the check, which should pass
    check = CheckAwsS3(name="Valid Bucket", value=bucket_name)
    result = check.check()
    assert result.passed

    # Validate the result of the first child check, CheckAwsS3BucketAccess,
    # which found an accessible bucket
    child_results = result.children
    assert child_results[0].passed
    assert child_results[0].status.startswith("passed")
