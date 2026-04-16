from __future__ import annotations

import math
import time
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Generic, TypeVar

from pulser.backend import Results, remote
from pulser_pasqal import PasqalCloud

ResultType = TypeVar("ResultType")


class JobFailedError(Exception):
    """Raised when a job reaches a failed or error state."""

    pass


class JobCancelledError(Exception):
    """Raised when a job was cancelled before or during execution."""

    pass


class JobStatus(Enum):
    """Represents the lifecycle state of a Job.

    Terminal states (where Job.is_done() returns True):
    - SUCCEEDED
    - FAILED
    - CANCELLED
    """

    PENDING = auto()
    """The job has been submitted but execution has not started yet."""

    RUNNING = auto()
    """The job is currently being executed."""

    SUCCEEDED = auto()
    """The job completed successfully."""

    FAILED = auto()
    """The job terminated due to a failure."""

    CANCELLED = auto()
    """The job was cancelled before or during execution."""


class Job(ABC, Generic[ResultType]):
    """Abstract representation of an asynchronous job or task.

    A Job tracks the lifecycle of a unit of work submitted for execution.
    It provides methods to inspect its state, wait for its result, and cancel it.

    Lifecycle:
        PENDING -> RUNNING -> SUCCEEDED
                           -> FAILED
                           -> CANCELLED
    """

    @abstractmethod
    def get_status(self) -> JobStatus:
        """Return the current status of the job."""
        ...

    @abstractmethod
    def id(self) -> str:
        """Return the unique identifier of the job."""
        ...

    @abstractmethod
    def result(self, timeout: float = math.inf, wait: float = 5) -> ResultType:
        """Block until the job completes and return its result.

        Args:
            timeout: Maximum seconds to wait. Defaults to math.inf (wait forever).
            wait: Polling interval in seconds. Defaults to 5.

        Raises:
            TimeoutError: If the job does not complete within timeout seconds.
            JobFailedError: If the job reached a failed or error state.
            JobCancelledError: If the job was cancelled.
        """
        ...

    @abstractmethod
    def message(self) -> str:
        """Return the latest status message, or an empty string if none."""
        ...

    @abstractmethod
    def cancel(self) -> None:
        """Request cancellation of the job.

        Has no effect if the job has already reached a terminal state.
        After cancellation, status() will return JobStatus.CANCELLED and done() will return True.
        """
        ...

    def is_done(self) -> bool:
        """Return True if the job has reached a terminal state (SUCCEEDED, FAILED, or CANCELLED)."""
        return self.get_status() in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}


class _LocalJob(Job[Results]):
    """Job implementation for local/synchronous execution."""

    def __init__(self, result: Results | None, message: str = "") -> None:
        super().__init__()
        self._result = result
        self._message = message

    def get_status(self) -> JobStatus:
        return JobStatus.FAILED if self._result is None else JobStatus.SUCCEEDED

    def id(self) -> str:
        # What should it be ?
        return ""

    def cancel(self) -> None:
        return

    def message(self) -> str:
        return self._message

    def result(self, timeout: float = math.inf, wait: float = 5) -> Results:
        status = self.get_status()
        if status == JobStatus.FAILED:
            raise JobFailedError(f"Job failed. Message: {self.message()}")
        assert status == JobStatus.SUCCEEDED
        return self._result


class _RemoteJob(Job[Results]):
    """Job implementation for remote/asynchronous execution."""

    _STATUS_MAP = {
        remote.JobStatus.PENDING: JobStatus.PENDING,
        remote.JobStatus.RUNNING: JobStatus.RUNNING,
        remote.JobStatus.DONE: JobStatus.SUCCEEDED,
        remote.JobStatus.CANCELED: JobStatus.CANCELLED,
        remote.JobStatus.ERROR: JobStatus.FAILED,
        remote.JobStatus.PAUSED: JobStatus.RUNNING,
    }

    def __init__(self, remote_results: remote.RemoteResults) -> None:
        super().__init__()
        self._remote_results = remote_results
        job_ids = self._remote_results.job_ids
        assert len(job_ids) > 0
        # If in open-batch mode, the job should be the last one in the batch ?
        self._id: str = job_ids[-1]

    def get_status(self) -> JobStatus:
        status = self._remote_results.get_status()
        if status not in self._STATUS_MAP:
            raise ValueError(f"Unhandled remote job status: {status!r}")
        return self._STATUS_MAP[status]

    def id(self) -> str:
        return self._id

    def cancel(self) -> None:
        return

    def message(self) -> str:
        return str(self._remote_results.batch_id)

    def result(self, timeout: float = math.inf, wait: float = 5) -> Results:
        # Back-off ? Inside connection, See pasqal-cloud
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status = self.get_status()
            if status == JobStatus.SUCCEEDED:
                return self._remote_results.results
            if status == JobStatus.FAILED:
                raise JobFailedError(f"Job {self.id()} failed.")
            if status == JobStatus.CANCELLED:
                raise JobCancelledError(f"Job {self.id()} was cancelled.")
            time.sleep(wait)
        raise TimeoutError(f"Job {self.id()} did not complete within {timeout} seconds.")


def retrieve_remote_job(id: str, connection: PasqalCloud) -> Job[Results]:
    # Is there a way to retrieve a job with _sdk_connection ?
    # Maybe input a sdk instead ?
    batch_id = connection._sdk_connection.get_job(id).batch_id
    remote_results = connection.get_results(batch_id, [id])
    return _RemoteJob(remote_results)
