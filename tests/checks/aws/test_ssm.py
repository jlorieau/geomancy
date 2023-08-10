"""Tests for aws.ssm"""
import pytest

from geomancy.checks.aws.ssm import CheckAwsSsmParameter


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset the caches for the CheckAwsSsmParameter"""
    # Reset the cache
    CheckAwsSsmParameter.get_parameters.cache_clear()


# This vcr cassette loads the '_cache' for CheckAwsSsmParameter, and it
# should be run first
@pytest.mark.vcr
def test_check_aws_ssm_valid():
    """Test CheckAwsSsmParameter for a valid parameter name"""
    # The cassette was loaded with a valid parameter
    parameter_name = "ValidParameter"

    # Run the check, which should pass
    check = CheckAwsSsmParameter(name="Valid Parameter", value=parameter_name)
    result = check.check()
    assert result.passed
    assert result.status == "passed"


@pytest.mark.vcr
def test_check_aws_ssm_missing():
    """Test CheckAwsSsmParameter for a missing parameter"""
    parameter_name = "mymissingparameter"

    # Run the check, which should not pass
    check = CheckAwsSsmParameter(name="Missing Parameter", value=parameter_name)
    result = check.check()
    assert not result.passed
    assert result.status == "failed (could not find 'mymissingparameter')"


@pytest.mark.vcr
def test_check_aws_ssm_invalid():
    """Test CheckAwsSsmParameter for an invalid parameter name"""
    parameter_name = "!invalid_name"

    # Run the check, which should not pass
    check = CheckAwsSsmParameter(name="Invalid Parameter", value=parameter_name)
    result = check.check()
    assert not result.passed
    assert result.status == "failed (could not find '!invalid_name')"


@pytest.mark.vcr
def test_check_aws_ssm_wrong_type():
    """Test CheckAwsSsmParameter for a parameter with the wrong type"""
    parameter_name = "ValidParameter"

    # Run the check, which should not pass
    check1 = CheckAwsSsmParameter(
        name="Wrong Type", value=parameter_name, type="SecureString"
    )
    result = check1.check()
    assert not result.passed
    assert result.status == (
        f"failed (parameter '{parameter_name}' has wrong type 'String')"
    )

    # Disabling the type check works
    check2 = CheckAwsSsmParameter(name="Wrong Type 2", value=parameter_name, type=None)
    assert check1 == check2

    result = check2.check()
    assert result.passed
    assert result.status == "passed"
