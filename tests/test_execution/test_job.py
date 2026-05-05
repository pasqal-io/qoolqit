from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pulser.backend import remote

from qoolqit.execution.job import (
    JobCancelledError,
    JobFailedError,
    JobStatus,
    _LocalJob,
    _RemoteJob,
    get_batch_id,
    retrieve_remote_job,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_remote_job(
    statuses: list[tuple[remote.JobStatus, object | None]],
    job_id: str = "job-123",
    batch_id: str = "batch-abc",
) -> _RemoteJob:
    """Return a _RemoteJob whose connection replays *statuses* in order."""
    connection = MagicMock(spec=remote.RemoteConnection)
    calls = iter(statuses)
    connection._query_job_progress.side_effect = lambda _batch_id: {job_id: next(calls)}
    return _RemoteJob(connection, job_id, batch_id=batch_id)


# ---------------------------------------------------------------------------
# JobStatus
# ---------------------------------------------------------------------------


class TestJobStatus:
    def test_is_alias_for_remote_job_status(self) -> None:
        assert JobStatus is remote.JobStatus

    def test_all_values_accessible(self) -> None:
        names = {s.name for s in JobStatus}
        assert {"PENDING", "RUNNING", "DONE", "ERROR", "CANCELED", "PAUSED"}.issubset(names)


# ---------------------------------------------------------------------------
# _LocalJob
# ---------------------------------------------------------------------------


class TestLocalJob:
    def test_done_when_result_provided(self) -> None:
        job = _LocalJob(MagicMock())
        assert job.get_status() == JobStatus.DONE

    def test_error_when_result_is_none(self) -> None:
        job = _LocalJob(None)
        assert job.get_status() == JobStatus.ERROR

    def test_has_ended_when_done(self) -> None:
        job = _LocalJob(MagicMock())
        assert job.has_ended()

    def test_has_ended_when_error(self) -> None:
        job = _LocalJob(None)
        assert job.has_ended()

    def test_results_returns_value(self) -> None:
        result = MagicMock()
        job = _LocalJob(result)
        assert job.results() is result

    def test_results_raises_on_failure(self) -> None:
        job = _LocalJob(None)
        with pytest.raises(JobFailedError):
            job.results()

    def test_results_ignores_timeout(self) -> None:
        result = MagicMock()
        job = _LocalJob(result)
        assert job.results(timeout=0) is result

    def test_job_id_is_empty_string(self) -> None:
        assert _LocalJob(MagicMock()).job_id() == ""

    def test_cancel_is_noop(self) -> None:
        _LocalJob(MagicMock()).cancel()  # must not raise


# ---------------------------------------------------------------------------
# _RemoteJob
# ---------------------------------------------------------------------------


class TestRemoteJob:
    def test_get_status_pending(self) -> None:
        job = make_remote_job([(remote.JobStatus.PENDING, None)])
        assert job.get_status() == JobStatus.PENDING

    def test_get_status_running(self) -> None:
        job = make_remote_job([(remote.JobStatus.RUNNING, None)])
        assert job.get_status() == JobStatus.RUNNING

    def test_get_status_done(self) -> None:
        job = make_remote_job([(remote.JobStatus.DONE, MagicMock())])
        assert job.get_status() == JobStatus.DONE

    def test_get_status_canceled(self) -> None:
        job = make_remote_job([(remote.JobStatus.CANCELED, None)])
        assert job.get_status() == JobStatus.CANCELED

    def test_get_status_error(self) -> None:
        job = make_remote_job([(remote.JobStatus.ERROR, None)])
        assert job.get_status() == JobStatus.ERROR

    def test_get_status_paused(self) -> None:
        job = make_remote_job([(remote.JobStatus.PAUSED, None)])
        assert job.get_status() == JobStatus.PAUSED

    def test_has_ended_false_while_pending(self) -> None:
        job = make_remote_job([(remote.JobStatus.PENDING, None)])
        assert not job.has_ended()

    def test_has_ended_false_while_running(self) -> None:
        job = make_remote_job([(remote.JobStatus.RUNNING, None)])
        assert not job.has_ended()

    def test_has_ended_false_while_paused(self) -> None:
        job = make_remote_job([(remote.JobStatus.PAUSED, None)])
        assert not job.has_ended()

    def test_has_ended_true_when_done(self) -> None:
        job = make_remote_job([(remote.JobStatus.DONE, MagicMock())])
        assert job.has_ended()

    def test_has_ended_true_when_error(self) -> None:
        job = make_remote_job([(remote.JobStatus.ERROR, None)])
        assert job.has_ended()

    def test_has_ended_true_when_canceled(self) -> None:
        job = make_remote_job([(remote.JobStatus.CANCELED, None)])
        assert job.has_ended()

    def test_results_returns_on_success(self) -> None:
        result = MagicMock()
        job = make_remote_job(
            [
                (remote.JobStatus.RUNNING, None),
                (remote.JobStatus.RUNNING, None),
                (remote.JobStatus.DONE, result),
            ]
        )
        assert job.results() is result

    def test_results_raises_on_failure(self) -> None:
        job = make_remote_job([(remote.JobStatus.ERROR, None)])
        with pytest.raises(JobFailedError):
            job.results()

    def test_results_raises_on_cancellation(self) -> None:
        job = make_remote_job([(remote.JobStatus.CANCELED, None)])
        with pytest.raises(JobCancelledError):
            job.results()

    def test_results_raises_timeout(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        connection._query_job_progress.return_value = {"job-123": (remote.JobStatus.RUNNING, None)}
        job = _RemoteJob(connection, "job-123", batch_id="batch-abc")
        with pytest.raises(TimeoutError, match="job-123"):
            job.results(timeout=0)

    def test_query_raises_if_job_id_not_found(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        connection._query_job_progress.return_value = {}
        job = _RemoteJob(connection, "missing-id", batch_id="b")
        with pytest.raises(ValueError, match="missing-id"):
            job.get_status()

    def test_job_id_returns_correct_value(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        job = _RemoteJob(connection, "my-id", batch_id="b")
        assert job.job_id() == "my-id"

    def test_cancel_is_noop(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        _RemoteJob(connection, "j", batch_id="b").cancel()  # must not raise

    def test_from_remote_results_selects_by_position(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        rr = MagicMock(spec=remote.RemoteResults, _connection=connection)
        rr.job_ids = ["job-0", "job-1", "job-2"]
        rr.batch_id = "batch-xyz"
        job = _RemoteJob._from_remote_results(rr, position=1)
        assert isinstance(job, _RemoteJob)
        assert job.job_id() == "job-1"
        assert job._batch_id == "batch-xyz"

    def test_from_remote_results_defaults_to_last(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        rr = MagicMock(spec=remote.RemoteResults, _connection=connection)
        rr.job_ids = ["job-0", "job-1"]
        rr.batch_id = "b"
        assert _RemoteJob._from_remote_results(rr).job_id() == "job-1"

    def test_from_remote_results_raises_on_bad_index(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        rr = MagicMock(spec=remote.RemoteResults, _connection=connection)
        rr.job_ids = []
        rr.batch_id = "b"
        with pytest.raises(IndexError):
            _RemoteJob._from_remote_results(rr, position=0)


# ---------------------------------------------------------------------------
# retrieve_remote_job
# ---------------------------------------------------------------------------


class TestRetrieveRemoteJob:
    def test_returns_remote_job_instance(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        job = retrieve_remote_job(connection, "job-id", batch_id="batch-id")
        assert isinstance(job, _RemoteJob)

    def test_job_id_and_batch_id_are_set(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        job = retrieve_remote_job(connection, "job-id", batch_id="batch-id")
        assert job.job_id() == "job-id"
        assert isinstance(job, _RemoteJob)
        assert job._batch_id == "batch-id"

    def test_batch_id_defaults_to_empty(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        job = retrieve_remote_job(connection, "job-id")
        assert isinstance(job, _RemoteJob)
        assert job._batch_id == ""


# ---------------------------------------------------------------------------
# get_batch_id
# ---------------------------------------------------------------------------


class TestGetBatchId:
    def test_returns_batch_id_for_remote_job(self) -> None:
        connection = MagicMock(spec=remote.RemoteConnection)
        job = _RemoteJob(connection, "j", batch_id="my-batch")
        assert get_batch_id(job) == "my-batch"

    def test_returns_empty_string_for_local_job(self) -> None:
        assert get_batch_id(_LocalJob(MagicMock())) == ""
