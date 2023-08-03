"""Tests for the CheckAWSIAM* classes"""
import pytest
import botocore.exceptions

from geomancy.checks.aws.iam import CheckAWSIAMAuthentication


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
