"""Fixtures for AWS tests"""
import re

import pytest


test_aws_username = "mytestuser"
test_aws_account_id = "8" * 12
test_aws_user_id = "X" * 20
test_aws_access_key = "Y" * 20
test_aws_secret_key = "S" * 40
test_aws_request_id = "99999999-9999-9999-9999-999999999999"


@pytest.fixture(scope="module")
def vcr_config(vcr_config):
    """VCR additional configuration for AWS"""

    # Scrub functions
    def scrub_request(request):
        """Script AWS PII from requence"""
        # Strip content-type headers
        request.headers.clear()

        # Replace body string
        if request.body is not None:
            body = request.body.decode("UTF-8")

            # username substitutions
            body = re.sub(r"(?<=UserName=)(\w+)", test_aws_username, body)

            request.body = body.encode("ascii")
        return request

    def scrub_response(response):
        """Scrub AWS PII from response"""
        # Remove unneeded header entries
        for entry in ("x-amz-request-id", "x-amz-id-2"):
            response["headers"].pop(entry, None)

        # Substitute strings in body
        body = response["body"]
        s = body["string"].decode("UTF-8")  # bytes -> string

        # username substitutions
        s = re.sub(r"(?<=user/)(\w+)", test_aws_username, s)
        s = re.sub(r"(?<=<UserName>)(\w+)", test_aws_username, s)

        # Account ID substitutions
        s = re.sub(r"\d{12}", test_aws_account_id, s)

        # User ID substitutions
        s = re.sub(r"AIDA[A-Z0-9]{1,124}", test_aws_account_id, s)  # User Id

        # Access Key ID substitutions
        s = re.sub(r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])", test_aws_access_key, s)

        # Secret Key ID substitutions
        s = re.sub(
            r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])",
            test_aws_secret_key,
            s,
        )

        # Request substitutions
        s = re.sub(
            r"(?<=<RequestId>)([a-f0-9\-]+)", test_aws_request_id, s
        )  # Request Id

        body["string"] = s.encode("ascii")  # string -> bytes

        # Replace or remove strings in headers
        response["headers"]["x-amzn-RequestId"] = test_aws_request_id
        return response

    vcr_config["before_record_request"] = scrub_request
    vcr_config["before_record_response"] = scrub_response
    return vcr_config


@pytest.fixture
def aws_invalid(monkeypatch):
    """Take a Monkeypatch context and load invalid AWS credentials"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "INVALID")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "INVALID")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "INVALID")
