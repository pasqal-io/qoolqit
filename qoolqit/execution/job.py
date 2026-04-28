from __future__ import annotations

import math
import time
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Generic, TypeVar

from pulser.backend import Results, remote

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
    def job_id(self) -> str:
        """Return the unique identifier of the job."""
        ...

    @abstractmethod
    def results(self, timeout: float = math.inf, wait: float = 5) -> ResultType:
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

    def job_id(self) -> str:
        # What should it be ?
        return ""

    def cancel(self) -> None:
        return

    def message(self) -> str:
        return self._message

    def results(self, timeout: float = math.inf, wait: float = 5) -> Results:
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

    def __init__(self, connection: remote.RemoteConnection, job_id: str, *, batch_id: str = "") -> None:
        super().__init__()
        self._connection = connection
        self._job_id = job_id
        self._batch_id = batch_id

    def _query_job_progress(self) -> tuple[JobStatus, Results | None]:
        jobs = self._connection._query_job_progress(self._batch_id)
        job_id = self.job_id()
        if job_id not in jobs.keys():
            raise ValueError(f"Job {job_id} not found")
        status, results = jobs[job_id]
        return self._STATUS_MAP[status], results


    def get_status(self) -> JobStatus:
        return self._query_job_progress()[0]

    def job_id(self) -> str:
        return self._id

    def cancel(self) -> None:
        return

    def message(self) -> str:
        return str(self._remote_results.batch_id)

    def results(self, timeout: float = math.inf, wait: float = 5) -> Results:
        # Back-off ? Inside connection, See pasqal-cloud
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status, results = self._query_job_progress()
            if status == JobStatus.SUCCEEDED:
                assert results is not None
                return results
            if status == JobStatus.FAILED:
                raise JobFailedError(f"Job {self.job_id()} failed.")
            if status == JobStatus.CANCELLED:
                raise JobCancelledError(f"Job {self.job_id()} was cancelled.")
            time.sleep(wait)
        raise TimeoutError(f"Job {self.job_id()} did not complete within {timeout} seconds.")

    @classmethod
    def _from_remote_results(cls, remote_results: remote.RemoteResults, position: int = -1) -> Job[Results]:
        connection = remote_results._connection
        try:
            job_id = remote_results.job_ids[position]
        except IndexError:
            raise IndexError(f"No job found at index {position} in the provided remote results.")
        batch_id = remote_results.batch_id
        return cls(connection, job_id, batch_id=batch_id)

def retrieve_remote_job(connection: remote.RemoteConnection, job_id: str, *, batch_id: str = "") -> Job[Results]:
    return _RemoteJob(connection, job_id, batch_id)

def get_batch_id(job: Job[Results]) -> str:
    if isinstance(job, _RemoteJob):
        return job._batch_id
    return ""
