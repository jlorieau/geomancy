"""Base class for AWS checks"""
import typing as t

from thatway import Setting

from ..base import Check, Result, Executor, CheckException

__all__ = ("CheckAws",)

#: The error message to show when AWS modules can't be imported
import_error_msg = (
    "The 'aws' dependency is not installed: {exception}. "
    "Please reinstall with the '[aws]' or '[all]' extra install "
    '`python -m pip install "geomancy[aws]"` or '
    '`python -m pip install "geomancy[all]"`'
)


class CheckAws(Check):
    """Abstract base class for AWS checks"""

    import_error_msg = import_error_msg

    #: Profile name to use to authenticate the AWS client, str
    profile: t.Optional[str]

    #: Default for profile
    profile_default = Setting(None, allowed_types=(None, str))

    def __init__(self, *args, profile: t.Optional[str] = None, **kwargs):
        self.profile = profile if profile is not None else self.profile_default
        super().__init__(*args, **kwargs)

    def client(self, *args, **kwargs) -> "botocore.client.BaseClient":
        """Retrieve the AWS client using the given profile.

        Raises
        ------
        CheckException
            The specified profile name could not be found
        """
        # Get the needed modules, profile name
        boto3, exceptions = self.import_modules("boto3", "botocore.exceptions")
        profile = kwargs.get("profile", self.profile)

        # Get a session
        try:
            session = (
                boto3.Session(profile_name=profile)
                if self.profile is not None
                else boto3.Session()
            )
        except exceptions.ProfileNotFound:
            raise CheckException("failed (profile not found)")

        return session.client(*args, **kwargs)

    def username(self, *args, **kwargs) -> str:
        """Retrieve the username of the current profile.

        Raises
        ------
        CheckException
            If the session profile was not found or the username could not be
            parsed
        """
        exceptions = self.import_modules("botocore.exceptions")

        iam = self.client("iam", *args, **kwargs)
        try:
            response = iam.get_user()
            return response["User"]["UserName"]
        except exceptions.ClientError:
            raise CheckException("failed (could not connect to client)")
        except KeyError:
            raise CheckException("failed (could not parse IAM.get_user())")

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        """Run sub-checks in sequence rather than concurrently, as done by the
        Check base class.

        This is done because the results of latter checks depend on earlier checks.
        """
        # check children
        child_results = []
        for child in self.children:
            result = child.check(executor=executor, level=level + 1)
            child_results.append(result)
            if not result.status.startswith("passed"):
                break

        return Result(
            msg=f"[bold]{self.name}[/bold]",
            children=child_results,
            condition=self.condition,
        )
