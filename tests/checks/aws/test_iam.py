"""Tests for the CheckAWSIAM* classes"""
import datetime
from unittest.mock import patch

import pytest

from geomancy.checks.aws.iam import CheckAWSIAMAuthentication, CheckAWSIAMAccessKeyAge


@pytest.mark.vcr
def test_check_aws_iam_authentication():
    """Test the CheckAWSIAMAuthentication check"""
    # 1. Test with an invalid profile
    profile = "invalid_profile"
    check = CheckAWSIAMAuthentication(name="Checker", profile=profile)
    assert check.profile == profile

    result = check.check()
    assert not result.passed
    assert result.status == "profile not found"

    # 2. Test with invalid keys
    with pytest.MonkeyPatch.context() as mp:
        # Invalid keys
        mp.setenv("AWS_ACCESS_KEY_ID", "INVALID")
        mp.setenv("AWS_SECRET_ACCESS_KEY", "INVALID")
        mp.setenv("AWS_SESSION_TOKEN", "INVALID")

        check = CheckAWSIAMAuthentication(name="Checker")
        assert check.profile is None

        result = check.check()
        assert not result.passed
        assert result.status == "could not authenticate with tokens"

    # 3. Test with a valid key
    check = CheckAWSIAMAuthentication(name="Checker")
    result = check.check()

    assert result.passed
    assert result.status.startswith("passed")


@pytest.mark.parametrize("age_days", (30, 120))
@pytest.mark.vcr
def test_check_aws_aim_access_key_age(age_days):
    """Test the CheckAWSIAMAccessKeyAge check"""
    # The following test was run with and the cassette modified to meet
    # the number of days in 'age_days'
    check = CheckAWSIAMAccessKeyAge(name="Access key age")

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
