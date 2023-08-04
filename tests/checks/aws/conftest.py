"""Fixtures for AWS tests"""
import pytest


@pytest.fixture
def aws_invalid(monkeypatch):
    """Take a Monkeypatch context and load invalid AWS credentials"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "INVALID")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "INVALID")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "INVALID")
