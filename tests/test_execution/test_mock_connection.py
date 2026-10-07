from __future__ import annotations

from collections.abc import Callable

import pulser
import pytest
from pulser.backend import EmulationConfig
from pulser.backend.default_observables import BitStrings
from pulser.backend.remote import BatchStatus, RemoteResults, RemoteResultsError
from pulser.backend.remote import JobStatus as PulserJobStatus
from pulser.backend.results import Results

from qoolqit import AnalogDevice, ConstantWaveform, Drive, QuantumProgram, Register
from qoolqit.execution import (
    JobStatus,
    LocalEmulationMockConnection,
    RemoteEmulator,
    get_batch_id,
    retrieve_remote_job,
)
from qoolqit.execution.mock_connection import _QUBIT_LIMIT

NUM_SHOTS = 50


def _program(*, n_qubits: int) -> QuantumProgram:
    register = Register.circle(n_qubits, spacing=1.1)
    drive = Drive(amplitude=ConstantWaveform(10.0, 0.1))
    program = QuantumProgram(register, drive)
    program.compile_to(AnalogDevice())
    return program


def _sequence(*, n_qubits: int) -> pulser.Sequence:
    return _program(n_qubits=n_qubits).compiled_sequence


def _config() -> EmulationConfig:
    return EmulationConfig(
        observables=[BitStrings(num_shots=NUM_SHOTS)], default_evaluation_times=[1.0]
    )


def test_submit_returns_completed_bitstring_results() -> None:
    remote_results = LocalEmulationMockConnection().submit(
        _sequence(n_qubits=3), backend_configuration=_config()
    )

    assert remote_results.get_batch_status() == BatchStatus.DONE
    assert len(remote_results.results) == 1

    results = remote_results.results[0]
    assert isinstance(results, Results)
    assert results.get_result_tags() == ["bitstrings"]

    counts = results.get_result("bitstrings", 1.0)
    assert sum(counts.values()) == NUM_SHOTS
    assert all(len(bitstring) == 3 for bitstring in counts)


def test_batch_holds_a_single_job() -> None:
    connection = LocalEmulationMockConnection()
    remote_results = connection.submit(_sequence(n_qubits=3), backend_configuration=_config())
    batch_id = remote_results.batch_id

    assert remote_results.job_ids == [f"{batch_id}-0"]
    assert connection._get_job_ids(batch_id) == [f"{batch_id}-0"]


def test_query_job_progress_reports_done_with_results() -> None:
    connection = LocalEmulationMockConnection()
    remote_results = connection.submit(_sequence(n_qubits=3), backend_configuration=_config())
    progress = connection._query_job_progress(remote_results.batch_id)

    assert list(progress) == remote_results.job_ids
    status, results = progress[remote_results.job_ids[0]]
    assert status == PulserJobStatus.DONE
    assert isinstance(results, Results)
    assert list(remote_results.get_available_results()) == remote_results.job_ids


def test_each_submission_creates_its_own_batch() -> None:
    connection = LocalEmulationMockConnection()
    sequence, config = _sequence(n_qubits=3), _config()

    first = connection.submit(sequence, backend_configuration=config)
    second = connection.submit(sequence, batch_id=first.batch_id, backend_configuration=config)

    # `batch_id` is ignored, so the second submission does not extend the first.
    assert first.batch_id != second.batch_id
    assert len(connection._batches) == 2
    assert len(second.results) == 1


def test_unknown_batch_reports_error_status() -> None:
    # A status query answers with a status rather than raising.
    assert LocalEmulationMockConnection()._get_batch_status("unknown") == BatchStatus.ERROR


def test_job_params_are_ignored() -> None:
    # A real connection runs one job per `job_params` entry, each sampled `runs` times.
    # Here the shot count comes from the emulation config only, and a batch always
    # holds a single job.
    remote_results = LocalEmulationMockConnection().submit(
        _sequence(n_qubits=3),
        job_params=[{"runs": 7}, {"runs": 7}],
        backend_configuration=_config(),
    )

    counts = remote_results.results[0].get_result("bitstrings", 1.0)
    assert sum(counts.values()) == NUM_SHOTS
    assert len(remote_results.job_ids) == 1
    assert len(remote_results.results) == 1


@pytest.mark.parametrize(
    "lookup",
    [
        lambda connection: connection._get_job_ids("unknown"),
        lambda connection: connection._fetch_result("unknown", None),
        lambda connection: connection._query_job_progress("unknown"),
        lambda connection: RemoteResults("unknown", connection, job_ids=["unknown-0"]),
    ],
    ids=["get_job_ids", "fetch_result", "query_job_progress", "remote_results"],
)
def test_unknown_batch_is_rejected(
    lookup: Callable[[LocalEmulationMockConnection], object],
) -> None:
    with pytest.raises(RemoteResultsError, match="Unknown batch 'unknown'"):
        lookup(LocalEmulationMockConnection())


def test_fetch_result_accepts_the_batch_own_job() -> None:
    connection = LocalEmulationMockConnection()
    remote_results = connection.submit(_sequence(n_qubits=3), backend_configuration=_config())
    batch_id = remote_results.batch_id

    assert len(connection._fetch_result(batch_id, None)) == 1
    assert len(connection._fetch_result(batch_id, connection._get_job_ids(batch_id))) == 1
    assert len(RemoteResults(batch_id, connection, job_ids=remote_results.job_ids).results) == 1


@pytest.mark.parametrize("job_ids", [["unknown"], []])
def test_fetch_result_rejects_foreign_jobs(job_ids: list[str]) -> None:
    connection = LocalEmulationMockConnection()
    remote_results = connection.submit(_sequence(n_qubits=3), backend_configuration=_config())

    with pytest.raises(RemoteResultsError, match="does not contain jobs"):
        connection._fetch_result(remote_results.batch_id, job_ids)


def test_open_batch_is_not_supported() -> None:
    connection = LocalEmulationMockConnection()
    assert not connection.supports_open_batch()

    with pytest.raises(NotImplementedError, match="open batches"):
        connection.submit(_sequence(n_qubits=3), open=True, backend_configuration=_config())


def test_too_many_qubits_is_not_supported() -> None:
    with pytest.raises(NotImplementedError, match=f"limit is {_QUBIT_LIMIT}"):
        LocalEmulationMockConnection().submit(
            _sequence(n_qubits=_QUBIT_LIMIT), backend_configuration=_config()
        )


@pytest.mark.parametrize("num_shots", [1, 20])
def test_runs_through_remote_emulator(num_shots: int) -> None:
    emulator = RemoteEmulator(connection=LocalEmulationMockConnection(), num_shots=num_shots)
    results = emulator.run(_program(n_qubits=3)).results()

    counts = results.get_result(results.get_result_tags()[0], 1.0)
    assert sum(counts.values()) == num_shots


def test_retrieve_remote_job() -> None:
    connection = LocalEmulationMockConnection()
    job = RemoteEmulator(connection=connection).run(_program(n_qubits=3))
    assert job.get_status() == JobStatus.DONE

    reloaded_job = retrieve_remote_job(connection, job.job_id(), batch_id=get_batch_id(job))
    assert reloaded_job.get_status() == JobStatus.DONE
    assert reloaded_job.results() == job.results()
