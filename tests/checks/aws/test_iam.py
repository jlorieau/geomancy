"""Tests for the CheckAWSIAM* classes"""
import datetime
from unittest.mock import patch

import pytest

from geomancy.checks.aws.base import CheckAws
from geomancy.checks.aws.iam import (
    CheckAwsIamAuthentication,
    CheckAwsIamRootAccess,
    CheckAwsIamAccessKeyAge,
    CheckAwsIam,
)


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset the caches for the CheckAwsIam"""
    # Reset the cache
    CheckAwsIam.username.cache_clear()


@pytest.mark.parametrize(
    "cls",
    (
        CheckAwsIam,
        CheckAwsIamAccessKeyAge,
        CheckAwsIamRootAccess,
        CheckAwsIamAuthentication,
    ),
)
def test_check_aws_iam_profile(cls):
    """Test that CheckAwsIam* profiles are properly loaded"""
    # Create the check with a custom profile
    custom_profile = "custom_profile"
    check = cls(name="CheckProfile", profile=custom_profile)

    assert check.profile == custom_profile

    # If the class has children (CheckAwsS3) check those too
    for child in check.children:
        if not isinstance(child, CheckAws):
            continue
        assert child.profile == custom_profile


@pytest.mark.vcr
def test_check_aws_iam_authentication():
    """Test the CheckAwsIamAuthentication check"""
    check = CheckAwsIamAuthentication(name="Checker")
    result = check.check()

    assert result.passed
    assert result.status.startswith("passed")


@pytest.mark.block_network
def test_check_aws_iam_authentication_invalid_profile():
    """Test the CheckAwsIamAuthentication check with and invalid profile"""
    # 1. Test with an invalid profile
    profile = "invalid_profile"
    check = CheckAwsIamAuthentication(name="Checker", profile=profile)
    assert check.profile == profile

    result = check.check()
    assert not result.passed
    assert result.status == "failed (profile not found)"


@pytest.mark.vcr
def test_check_aws_iam_authentication_invalid_keys(aws_invalid):
    """Test the CheckAwsIamAuthentication check with invalid AWS keys"""
    check = CheckAwsIamAuthentication(name="Checker")
    assert check.profile is None

    result = check.check()
    assert not result.passed
    assert result.status == "failed (can't authenticate with given tokens)"


@pytest.mark.parametrize("mode", ("has_root_keys", "has_signing_certs", "neither"))
@pytest.mark.vcr
def test_check_aws_iam_root_access(mode):
    """Test the CheckAwsIamRootAccess check"""
    check = CheckAwsIamRootAccess(name="CheckRoot")
    result = check.check()

    if mode == "has_root_keys":
        assert not result.passed
        assert result.status == "failed (account has root access keys)"
    elif mode == "has_signing_certs":
        assert not result.passed
        assert result.status == "failed (account has signing certificates)"
    else:
        assert result.passed


@pytest.mark.parametrize("age_days", (30, 120))
@pytest.mark.vcr
def test_check_aws_iam_access_key_age(age_days):
    """Test the CheckAwsIamAccessKeyAge check"""
    # The following test was run with and the cassette modified to meet
    # the number of days in 'age_days'
    check = CheckAwsIamAccessKeyAge(name="AccessKeyAge")

    # Create a mockdatetime to pin a date
    class mockdatetime(datetime.datetime):
        @classmethod
        def now(cls, *args, **kwargs):
            return datetime.datetime(2023, 8, 4, 5, 31, 11, 895114)

    # Run the check with a pinned date/time
    with patch("geomancy.checks.aws.iam.datetime.datetime", mockdatetime):
        result = check.check()

    # Check the age in days
    if age_days < 90:
        assert result.passed
    else:
        assert not result.passed


@pytest.mark.vcr
def test_check_aws_iam():
    """Test the CheckAwsIam check with a valid profile"""
    check = CheckAwsIam(name="CheckIAM")

    # By default, the other CheckAwsIam classes should be children
    for cls in (
        CheckAwsIamAccessKeyAge,
        CheckAwsIamRootAccess,
        CheckAwsIamAuthentication,
    ):
        assert cls in [type(child) for child in check.children]

    # The test should pass normally for a valid profile (see cassette)
    result = check.check()
    assert result.passed
