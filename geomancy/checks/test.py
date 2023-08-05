"""Check classes to test running checks"""
import typing as t
import time

from .base import Check, Result, Executor


class CheckSleep(Check):
    """A check that sleeps for a specified about of time"""

    #: Time in seconds to sleep the check
    sleep: int = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep = int(self.value)

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        time.sleep(self.sleep)
        return Result(status="passed", msg="" f"{self.name} sleeping for {self.sleep}s")
