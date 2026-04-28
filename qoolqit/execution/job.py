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


class JobCancelledError(Exception):
    """Raised when a job was cancelled before or during execution."""


class JobStatus(Enum):
    """Lifecycle state of a :class:`Job`.

    Terminal states (where :meth:`Job.is_done` returns ``True``):

    - :attr:`SUCCEEDED`
    - :attr:`FAILED`
    - :attr:`CANCELLED`
    """

    PENDING = auto()
    """Job submitted but execution has not started yet."""

    RUNNING = auto()
    """Job is currently being executed."""

    SUCCEEDED = auto()
    """Job completed successfully."""

    FAILED = auto()
    """Job terminated due to a failure."""

    CANCELLED = auto()
    """Job was cancelled before or during execution."""


class Job(ABC, Generic[ResultType]):
    """Abstract representation of an asynchronous job or task.

    A :class:`Job` tracks the lifecycle of a unit of work submitted
    for execution. It provides methods to inspect its state, wait for
    its result, and cancel it.

    Lifecycle::

        PENDING -> RUNNING -> SUCCEEDED
                           -> FAILED
                           -> CANCELLED

    Concrete backend implementations (:class:`_LocalJob`,
    :class:`_RemoteJob`) must override all abstract methods.
    End users should never instantiate subclasses directly;
    instead, obtain a :class:`Job` from a backend submission
    function such as ``backend.run(program)``.

    Note:
        A submitted job is not necessarily asynchronous. Whether
        execution is synchronous or asynchronous depends on the
        function that creates and returns the :class:`Job` instance
        (e.g. a local backend may execute synchronously and return
        an already-completed job, while a remote backend submits
        the work and returns a job that must be polled).
    """

    @abstractmethod
    def get_status(self) -> JobStatus:
        """Return the current lifecycle state of the job.

        Returns:
            JobStatus: The current state of the job.
        """
        ...

    @abstractmethod
    def job_id(self) -> str:
        """Return the unique identifier of the job.

        For remote jobs this is the UUID used to track the job in
        the PASQAL Cloud Portal. For local jobs this is currently
        an empty string.

        Returns:
            str: A string uniquely identifying this job.
        """
        ...

    @abstractmethod
    def results(
        self, timeout: float = math.inf
    ) -> ResultType:
        """Block until the job completes and return its result.

        Waits until the job reaches a terminal state, then returns
        the result. Polling strategy (interval, backoff) is delegated
        to the underlying connection.

        Args:
            timeout (float): Maximum seconds to wait.
                Defaults to ``math.inf`` (wait indefinitely).

        Returns:
            ResultType: The result produced by the job.

        Raises:
            TimeoutError: If the job does not complete within
                *timeout* seconds.
            JobFailedError: If the job reached a failed or error state.
            JobCancelledError: If the job was cancelled.
        """
        ...

    @abstractmethod
    def message(self) -> str:
        """Return the latest human-readable status message.

        Provides details about the job's current state or completion
        reason (e.g. an error description).

        Returns:
            str: The latest status message, or an empty string if
            none is available.
        """
        ...

    @abstractmethod
    def cancel(self) -> None:
        """Request cancellation of the job.

        Has no effect if the job has already reached a terminal state.
        After a successful cancellation, :meth:`get_status` returns
        :attr:`JobStatus.CANCELLED` and :meth:`is_done` returns
        ``True``.

        Note:
            Some implementations do not support cancellation. In that
            case this method is a no-op and the job status will never
            be :attr:`JobStatus.CANCELLED`.
        """
        ...

    def is_done(self) -> bool:
        """Return whether the job has reached a terminal state.

        A job is done when its status is one of
        :attr:`~JobStatus.SUCCEEDED`, :attr:`~JobStatus.FAILED`, or
        :attr:`~JobStatus.CANCELLED`.

        Returns:
            bool: ``True`` if the job is in a terminal state,
            ``False`` otherwise.
        """
        return self.get_status() in {
            JobStatus.SUCCEEDED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        }


class _LocalJob(Job[Results]):
    """Job implementation for local/synchronous execution.

    The result is determined at construction time: if *result* is
    ``None`` the job is considered failed; otherwise it is considered
    succeeded. :meth:`results` therefore returns immediately without
    any polling.

    Note:
        This class is private. Do not instantiate it directly.
        Obtain instances from the local backend's submission function.

    Args:
        result (Results | None): The result of local execution,
            or ``None`` if execution failed.
        message (str): Optional human-readable status message.
            Defaults to an empty string.
    """

    def __init__(self, result: Results | None, message: str = "") -> None:
        super().__init__()
        self._result = result
        self._message = message

    def get_status(self) -> JobStatus:
        """Return FAILED if *result* is ``None``, otherwise SUCCEEDED."""
        return JobStatus.FAILED if self._result is None else JobStatus.SUCCEEDED

    def job_id(self) -> str:
        """Return the job identifier.

        Note:
            Local jobs do not currently have a meaningful identifier.
            This method returns an empty string.

        Returns:
            str: An empty string.
        """
        return ""

    def cancel(self) -> None:
        """No-op: local jobs complete synchronously and cannot be cancelled."""
        return

    def message(self) -> str:
        """Return the status message provided at construction time.

        Returns:
            str: The message string, or an empty string if none.
        """
        return self._message

    def results(self, timeout: float = math.inf) -> Results:
        """Return the local execution result immediately.

        The *timeout* argument is accepted for API compatibility but
        is ignored because local execution is synchronous.

        Args:
            timeout (float): Ignored for local jobs.

        Returns:
            Results: The result of the local execution.

        Raises:
            JobFailedError: If the job failed (i.e. *result* was
                ``None`` at construction time).
        """
        status = self.get_status()
        if status == JobStatus.FAILED:
            raise JobFailedError(f"Job failed. Message: {self.message()}")
        assert status == JobStatus.SUCCEEDED
        return self._result


class _RemoteJob(Job[Results]):
    """Job implementation for remote/asynchronous execution.

    Polls the remote connection for status updates until the job
    reaches a terminal state. Status values from Pulser's
    :class:`~pulser.backend.remote.RemoteConnection` are translated
    to :class:`JobStatus` via :attr:`_STATUS_MAP`.

    Note:
        This class is private. Do not instantiate it directly.
        Obtain instances via :func:`retrieve_remote_job` or
        :meth:`_from_remote_results`.

    Args:
        connection (remote.RemoteConnection): The connection used to
            query job progress and results.
        job_id (str): The unique identifier of the remote job.
        batch_id (str): The batch identifier the job belongs to.
            Required by some RemoteConnection implementations to query
            job progress. Defaults to an empty string.
    """

    _STATUS_MAP = {
        remote.JobStatus.PENDING: JobStatus.PENDING,
        remote.JobStatus.RUNNING: JobStatus.RUNNING,
        remote.JobStatus.DONE: JobStatus.SUCCEEDED,
        remote.JobStatus.CANCELED: JobStatus.CANCELLED,
        remote.JobStatus.ERROR: JobStatus.FAILED,
        remote.JobStatus.PAUSED: JobStatus.RUNNING,
    }
    """Mapping from Pulser's JobStatus values to :class:`JobStatus`."""

    def __init__(
        self,
        connection: remote.RemoteConnection,
        job_id: str,
        *,
        batch_id: str = "",
    ) -> None:
        super().__init__()
        self._connection = connection
        self._job_id = job_id
        self._batch_id = batch_id

    def _query_job_progress(self) -> tuple[JobStatus, Results | None]:
        """Query the remote connection for the current status and results.

        Returns:
            tuple[JobStatus, Results | None]: A ``(status, results)``
            pair. *results* is ``None`` unless the job has succeeded.

        Raises:
            ValueError: If the job ID is not found in the batch
                returned by the connection.
        """
        jobs = self._connection._query_job_progress(self._batch_id)
        job_id = self.job_id()
        if job_id not in jobs:
            raise ValueError(f"Job {job_id} not found")
        status, results = jobs[job_id]
        return self._STATUS_MAP[status], results

    def get_status(self) -> JobStatus:
        """Query the remote connection and return the current job status.

        Returns:
            JobStatus: The current lifecycle state of the job.
        """
        return self._query_job_progress()[0]

    def job_id(self) -> str:
        """Return the unique identifier of the remote job.

        Returns:
            str: The job UUID string.
        """
        return self._job_id

    def cancel(self) -> None:
        """Request cancellation of the job.

        Note:
            Cancellation is not yet implemented for remote jobs.
        """
        return

    def message(self) -> str:
        """Return the batch ID as a status message.

        Returns:
            str: String representation of the batch ID.
        """
        return ""

    def results(self, timeout: float = math.inf) -> Results:
        """Block until the remote job completes and return its result.

        Repeatedly calls :meth:`_query_job_progress` until the job
        reaches a terminal state or *timeout* expires. Polling
        interval and backoff are delegated to the connection.

        Args:
            timeout (float): Maximum seconds to wait.
                Defaults to ``math.inf`` (wait indefinitely).

        Returns:
            Results: The result produced by the remote job.

        Raises:
            TimeoutError: If the job does not complete within *timeout*
                seconds.
            JobFailedError: If the job reached FAILED status.
            JobCancelledError: If the job was CANCELLED.
        """
        deadline = time.monotonic() + timeout
        while True:
            status, results = self._query_job_progress()
            if status == JobStatus.SUCCEEDED:
                assert results is not None
                return results
            if status == JobStatus.FAILED:
                raise JobFailedError(f"Job {self.job_id()} failed.")
            if status == JobStatus.CANCELLED:
                raise JobCancelledError(f"Job {self.job_id()} was cancelled.")
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Job {self.job_id()} did not complete within {timeout} seconds."
        )

    @classmethod
    def _from_remote_results(
        cls,
        remote_results: remote.RemoteResults,
        position: int = -1,
    ) -> Job[Results]:
        """Construct a :class:`_RemoteJob` from a RemoteResults object.

        Extracts the connection, job ID, and batch ID from an existing
        :class:`~pulser.backend.remote.RemoteResults` instance.

        Args:
            remote_results (remote.RemoteResults): The RemoteResults
                object returned by a Pulser backend submission.
            position (int): Index into ``remote_results.job_ids`` to
                select the job. Defaults to ``-1`` (last job).

        Returns:
            Job[Results]: A :class:`_RemoteJob` connected to the
            selected job.

        Raises:
            IndexError: If *position* is out of range for
                ``remote_results.job_ids``.
        """
        connection = remote_results._connection
        try:
            job_id = remote_results.job_ids[position]
        except IndexError:
            raise IndexError(
                f"No job found at index {position} in the provided remote results."
            )
        batch_id = remote_results.batch_id
        return cls(connection, job_id, batch_id=batch_id)


def retrieve_remote_job(
    connection: remote.RemoteConnection,
    job_id: str,
    *,
    batch_id: str = "",
) -> Job[Results]:
    """Retrieve a previously submitted remote job by its identifiers.

    Use this to reconnect to a job in a new session, or to monitor a
    job submitted outside the current context.

    Note:
        The *batch_id* argument is required by some
        ``RemoteConnection`` implementations (e.g.
        ``PasqalCloudConnection``) to query job progress. Use
        :func:`get_batch_id` to recover the batch ID from an existing
        :class:`Job` if needed.

        This dependency on *batch_id* is temporary and will be removed
        once ``RemoteConnection`` supports direct lookup by job ID
        alone.

    Args:
        connection (remote.RemoteConnection): The remote connection
            through which to query the job.
        job_id (str): The UUID of the job to retrieve.
        batch_id (str): The batch identifier the job belongs to.
            Defaults to an empty string.

    Returns:
        Job[Results]: A :class:`_RemoteJob` connected to the
        specified job.
    """
    return _RemoteJob(connection, job_id, batch_id=batch_id)


def get_batch_id(job: Job[Results]) -> str:
    """Return the batch ID associated with a remote job.

    Temporary utility for cases where *batch_id* must be persisted
    and later passed to :func:`retrieve_remote_job`. Will be
    deprecated once ``RemoteConnection`` supports direct job lookup
    by job ID alone.

    Args:
        job (Job[Results]): Any :class:`Job` instance.

    Returns:
        str: The batch ID if *job* is a :class:`_RemoteJob`,
        otherwise an empty string.
    """
    if isinstance(job, _RemoteJob):
        return job._batch_id
    return ""
