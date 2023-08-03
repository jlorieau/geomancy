"""Base class for AWS checks"""
import typing as t
from abc import ABC, abstractmethod

from ..base import Check, Result, Executor
from ...config import Parameter


#: The error message to show when AWS modules can't be imported
import_error_msg = (
    "The 'aws' dependency is not installed: {exception}. "
    "Please reinstall with the '[aws]' or '[all]' extra install "
    '`python -m pip install "geomancy[aws]"` or '
    '`python -m pip install "geomancy[all]"`'
)


class CheckAWS(Check, ABC):
    """Abstract base class for AWS checks"""

    #: Profile name to use to authenticate the AWS client, str
    profile_default = Parameter("CHECKAWS.PROFILE", None)

    def __init__(self, *args, profile: t.Optional[str] = None, **kwargs):
        self.profile = profile if profile is not None else self.profile_default
        super().__init__(*args, **kwargs)

    def client(self, *args, **kwargs):
        """Retrieve the AWS client using the given profile.

        Raises
        ------
        botocore.exceptions.ProfileNotFound
            The specified profile name could not be found
        """
        # Get the needed modules, bucket name and boto3 client
        boto3 = self.import_modules("boto3")

        # Get a session
        session = (
            boto3.Session(profile_name=self.profile)
            if self.profile is not None
            else boto3.Session()
        )
        return session.client(*args, **kwargs)

    @abstractmethod
    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        pass
