"""Backends to run quantum programs on local/remote emulators and QPUs.

Pulser backends require a compiled sequence at initialization. QoolQit backends
lift this limitation: they instantiate the underlying Pulser backend in `run`,
from the `QuantumProgram` being executed, so the same backend can run many programs.
"""

from __future__ import annotations

from pasqal_cloud.backends import RemoteEmuFreeBackend, RemoteEmulatorBackend
from pulser.backend import BackendConfig, BitStrings, Results
from pulser.backend.abc import EmulatorBackend
from pulser.backend.config import EmulationConfig
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import RemoteConnection
from pulser_simulation import QutipBackendV2

from qoolqit.execution import job
from qoolqit.program import QuantumProgram


class PulserEmulatorBackend:
    """Base class for QoolQit emulator backends (local and remote).

    Provides the shared emulation config handling, ensuring bitstrings are always sampled.

    Args:
        num_shots: number of bitstrings sampled from the final quantum state.
            If None, the `default_num_shots` of the emulation config is used (1000 by default).
    """

    def __init__(self, num_shots: int | None = None) -> None:
        """Initialize the backend with the number of shots."""
        self._num_shots = num_shots

    def validate_emulation_config(
        self, emulation_config: EmulationConfig | None
    ) -> EmulationConfig:
        """Return a valid emulation config, ensuring bitstrings are sampled.

        Args:
            emulation_config: optional emulation config.
                If None, `default_emulation_config` is used.

        Returns:
            The default config if `emulation_config` is None. Otherwise `emulation_config`,
            with a `BitStrings` observable added if missing. In both cases, `default_num_shots`
            is set to `num_shots` when provided.
        """
        if emulation_config is None:
            emulation_config = self.default_emulation_config()
        else:
            has_bitstrings = any(
                isinstance(obs, BitStrings) for obs in emulation_config.observables
            )
            if not has_bitstrings:
                updated_obs = (*emulation_config.observables, BitStrings(num_shots=self._num_shots))
                emulation_config = emulation_config.with_changes(observables=updated_obs)

        if self._num_shots is not None:
            emulation_config = emulation_config.with_changes(default_num_shots=self._num_shots)

        return emulation_config

    def default_emulation_config(self) -> EmulationConfig:
        """Return the default emulation config, shared by all emulators.

        It only asks for the final bitstrings, sampled `num_shots` times.
        """
        return EmulationConfig(observables=(BitStrings(num_shots=self._num_shots),))


class PulserRemoteBackend:
    """Base class for QoolQit remote backends (remote emulators and QPUs).

    Provides validation of the `RemoteConnection` used to submit jobs.
    """

    @staticmethod
    def validate_connection(connection: RemoteConnection) -> RemoteConnection:
        """Validate the connection required by remote emulators and QPUs.

        Remote emulators and QPUs require a `pulser.backend.remote.RemoteConnection`, or a
        subclass, to send jobs. Validation also happens inside the backend. Early validation
        just makes the error easier to understand.

        Args:
            connection: the connection to validate.

        Returns:
            The same `connection`, if valid.

        Raises:
            TypeError: if `connection` is not a `RemoteConnection`.
        """
        if not isinstance(connection, RemoteConnection):
            raise TypeError(f"""Error in `PulserRemoteBackend`:
                `connection` must be of type {RemoteConnection}.""")
        return connection


class LocalEmulator(PulserEmulatorBackend):
    """Run QoolQit `QuantumProgram`s on Pasqal local emulator backends.

    Args:
        backend_type: backend type. Must be a subtype of `pulser.backend.EmulatorBackend`.
        emulation_config: optional emulation config.
            If None, `default_emulation_config` is used.
        num_shots: number of bitstrings sampled from the final quantum state.
            If None, the `default_num_shots` of the emulation config is used (1000 by default).

    Examples:
        ```python
        from qoolqit.execution import LocalEmulator, BackendType
        backend = LocalEmulator(backend_type=BackendType.QutipBackendV2)
        job = backend.run(program)
        results = job.results()
        ```
    """

    def __init__(
        self,
        *,
        backend_type: type[EmulatorBackend] = QutipBackendV2,
        emulation_config: EmulationConfig | None = None,
        num_shots: int | None = None,
    ) -> None:
        """Instantiate a LocalEmulator."""
        super().__init__(num_shots=num_shots)
        if not issubclass(backend_type, EmulatorBackend):
            raise TypeError(
                "Error in `LocalEmulator`: `backend_type` must be a EmulatorBackend type."
            )
        self._backend_type = backend_type
        self._emulation_config = self.validate_emulation_config(emulation_config)

    def run(self, program: QuantumProgram) -> job.Job[Results]:
        """Run a compiled QuantumProgram and return a job handler.

        Args:
            program: the compiled quantum program to run.

        Returns:
            A `Job` handler, to retrieve the results with `job.results()`.
        """
        self._backend = self._backend_type(program.compiled_sequence, config=self._emulation_config)
        results = self._backend.run()
        assert isinstance(results, Results)
        return job._LocalJob(results)


class RemoteEmulator(PulserEmulatorBackend, PulserRemoteBackend):
    """Run QoolQit `QuantumProgram`s on Pasqal remote emulator backends.

    Works like `LocalEmulator`, but requires an authenticated `connection`.
    See the [Pasqal Cloud documentation](https://docs.pasqal.com/cloud/set-up/)
    to get credentials and create one.

    Args:
        backend_type: backend type. Must be a subtype of
            `pasqal_cloud.backends.RemoteEmulatorBackend`.
        connection: connection to execute the program on remote backends.
        emulation_config: optional emulation config.
            If None, `default_emulation_config` is used.
        num_shots: number of bitstrings sampled from the final quantum state.
            If None, the `default_num_shots` of the emulation config is used (1000 by default).

    Examples:
        ```python
        from pasqal_cloud import PasqalCloudConnection
        from qoolqit.execution import RemoteEmulator, BackendType
        connection = PasqalCloudConnection(username=..., password=..., project_id=...)
        backend = RemoteEmulator(
            backend_type=BackendType.RemoteEmuFreeBackend, connection=connection
        )
        job = backend.run(program)
        ```
        See `run` to retrieve the results.
    """

    def __init__(
        self,
        *,
        backend_type: type[RemoteEmulatorBackend] = RemoteEmuFreeBackend,
        connection: RemoteConnection,
        emulation_config: EmulationConfig | None = None,
        num_shots: int | None = None,
    ) -> None:
        """Instantiate a RemoteEmulator."""
        super().__init__(num_shots=num_shots)
        if not issubclass(backend_type, RemoteEmulatorBackend):
            raise TypeError(
                "Error in `RemoteEmulator`: `backend_type` must be a RemoteEmulatorBackend type."
            )
        self._backend_type = backend_type
        self._connection = self.validate_connection(connection)
        self._emulation_config = self.validate_emulation_config(emulation_config)

    def run(self, program: QuantumProgram) -> job.Job[Results]:
        """Submit a compiled QuantumProgram and return a job handler.

        `run` returns as soon as the job is submitted, the job runs remotely.

        Args:
            program: the compiled quantum program to run.

        Returns:
            A `Job` handler, to check the status and retrieve the results.

        Examples:
            Wait for the results, with a timeout. On timeout the job keeps running,
            and `job.results()` can be called again later:
            ```python
            job = backend.run(program)
            try:
                results = job.results(timeout=600)
            except TimeoutError:
                print(f"Job {job.job_id()} still running")
            ```

            Check the status without blocking:
            ```python
            job = backend.run(program)
            job.get_status()  # e.g. JobStatus.PENDING
            job.has_ended()  # True once DONE, ERROR or CANCELED
            results = job.results()  # blocks until the job has ended
            ```

            Reconnect later, for long jobs (e.g. QPU queues), possibly from a new session:
            ```python
            from qoolqit.execution import get_batch_id, retrieve_remote_job
            job = backend.run(program)
            job_id, batch_id = job.job_id(), get_batch_id(job)  # store these
            # later
            job = retrieve_remote_job(connection, job_id, batch_id=batch_id)
            results = job.results()
            ```
        """
        self._backend = self._backend_type(
            program.compiled_sequence,
            connection=self._connection,
            config=self._emulation_config,
        )
        remote_results = self._backend.run(wait=False)
        # Each run submits a single job, in a new batch.
        return job._RemoteJob._from_remote_results(remote_results)


class QPU(PulserRemoteBackend):
    """Execute QoolQit QuantumPrograms on Pasqal quantum processing units.

    Runs on actual QPU hardware and requires an authenticated `connection`.

    Args:
        connection: Authenticated connection to the remote QPU backend.
        num_shots: Number of runs of the program on the QPU. Required.

    Examples:
        Using Pasqal Cloud:
        ```python
        from pasqal_cloud import PasqalCloudConnection
        from qoolqit.execution import QPU
        connection = PasqalCloudConnection(username=..., password=..., project_id=...)
        backend = QPU(connection=connection, num_shots=100)
        job = backend.run(program)
        ```

        Using Atos MyQLM:
        ```python
        from pulser_myqlm import PulserQLMConnection
        from qoolqit.execution import QPU
        connection = PulserQLMConnection()
        backend = QPU(connection=connection, num_shots=100)
        job = backend.run(program)
        ```
        See `run` to retrieve the results.

    Note:
        Contact your quantum computing provider for credentials and connection setup:
        - [Pasqal Cloud Documentation](https://docs.pasqal.com/cloud/set-up/)
        - [Atos MyQML Framework](https://github.com/pasqal-io/Pulser-myQLM)
    """

    def __init__(
        self,
        *,
        connection: RemoteConnection,
        num_shots: int | None = None,
    ) -> None:
        """Instantiate a QPU backend."""
        self._backend_type = QPUBackend
        self._connection = self.validate_connection(connection)
        if num_shots is None:
            raise ValueError(
                """Number of shots must be provided to use the QPU backend.
                Please specify `num_shots` when creating the QPU instance.
                For example: QPU(connection=..., num_shots=100)""",
            )
        self._config = BackendConfig(default_num_shots=num_shots)

    def run(self, program: QuantumProgram) -> job.Job[Results]:
        """Submit a compiled QuantumProgram and return a job handler.

        `run` returns as soon as the job is submitted, the job runs remotely.

        Args:
            program: the compiled quantum program to run.

        Returns:
            A `Job` handler, to check the status and retrieve the results.

        Examples:
            Wait for the results, with a timeout. On timeout the job keeps running,
            and `job.results()` can be called again later:
            ```python
            job = backend.run(program)
            try:
                results = job.results(timeout=600)
            except TimeoutError:
                print(f"Job {job.job_id()} still running")
            ```

            Check the status without blocking:
            ```python
            job = backend.run(program)
            job.get_status()  # e.g. JobStatus.PENDING
            job.has_ended()  # True once DONE, ERROR or CANCELED
            results = job.results()  # blocks until the job has ended
            ```

            Reconnect later, for long jobs (e.g. QPU queues), possibly from a new session:
            ```python
            from qoolqit.execution import get_batch_id, retrieve_remote_job
            job = backend.run(program)
            job_id, batch_id = job.job_id(), get_batch_id(job)  # store these
            # later
            job = retrieve_remote_job(connection, job_id, batch_id=batch_id)
            results = job.results()
            ```
        """
        self._backend = self._backend_type(
            program.compiled_sequence, connection=self._connection, config=self._config
        )
        remote_results = self._backend.run(wait=False)
        # Each run submits a single job, in a new batch.
        return job._RemoteJob._from_remote_results(remote_results)
