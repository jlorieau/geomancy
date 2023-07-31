"""Fixtures for project testing"""
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    """A fixture to configure pytest-recording"""
    return {
        "filter_headers": [
            "authorization",
            "User-Agent",
            "X-Amz-Date",
            "X-Amz-Content-SHA256",
            "amz-sdk-invocation-id",
            "amz-sdk-request",
        ]
    }


@pytest.fixture
def test_env_file() -> dict:
    """Filename and expected values for the 'environment/test.env' file."""
    return {
        "filepath": str(Path(__file__).parent / "data" / "test.env"),
        "variables": {
            "VALUE1": "My Value",
            "VALUE2": "dev",
            "VALUE3": "my-dev",
            "VALUE4": "A Multiline\nenvironment variable",
            "VALUE5": "Extra endspaces removed",
        },
    }
