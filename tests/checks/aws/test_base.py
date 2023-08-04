"""Test the functionality of CheckAws"""
import pytest

from geomancy.checks.aws.base import CheckAws, CheckException


@pytest.mark.block_network
def test_check_aws_client():
    """Test the CheckAws base class client method"""
    # 1. Test with an invalid profile
    profile = "invalid_profile"
    check = CheckAws(name="CheckAws", profile=profile)
    assert check.profile == profile

    with pytest.raises(CheckException, match="profile not found"):
        check.client("s3")

    # 2. The default should return a valid client
    check = CheckAws(name="CheckAws")
    check.client("s3")


# noinspection GrazieInspection
@pytest.mark.block_network
def test_check_aws_username_invalid_profile():
    """Test the CheckAws.username() method with an invalid profile"""
    profile = "invalid_profile"
    check = CheckAws(name="CheckAws", profile=profile)

    with pytest.raises(CheckException, match="profile not found"):
        check.username()


# noinspection GrazieInspection
@pytest.mark.vcr
def test_check_aws_username_invalid_keys(aws_invalid):
    """Test the CheckAws.username() method with invalid AWS keys"""
    check = CheckAws(name="CheckAws")

    with pytest.raises(CheckException, match="could not connect to client"):
        check.username()


# noinspection GrazieInspection
@pytest.mark.vcr
def test_check_aws_username():
    """Test the CheckAws.username() method with valid credentials"""
    check = CheckAws(name="CheckAws")
    assert check.username() == "mytestuser"
