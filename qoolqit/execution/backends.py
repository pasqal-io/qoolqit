from __future__ import annotations

from typing import Sequence

from pulser.backend import BackendConfig, BitStrings, Results
from pulser.backend.abc import EmulatorBackend
from pulser.backend.config import EmulationConfig
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import RemoteConnection, RemoteResults
from pulser_pasqal.backends import EmuFreeBackendV2, RemoteEmulatorBackend
from pulser_simulation import QutipBackendV2

from qoolqit.program import QuantumProgram


class PulserEmulatorBackend:
    """Base Emulator class.

    Args:
        runs: run the program `runs` times to collect bitstrings statistics.
            On QPU backends this represents the actual number of runs of the program.
            On emulators, instead the bitstring are sampled from the quantum state `runs` times.
    """

    def __init__(self, runs: int | None = None) -> None:
        self._runs = runs

    def validate_emulation_config(
        self, emulation_config: EmulationConfig | None
    ) -> EmulationConfig:
        """Returns a valid config for emulator backends, if needed.

        Args:
            emulation_config: optional base configuration class for all emulators backends.
                If no config is provided to an emulator backend, the backend default will used.
        """
        if emulation_config is None:
            emulation_config = self.default_emulation_config()
        else:
            has_bitstrings = any(
                isinstance(obs, BitStrings) for obs in emulation_config.observables
            )
            if not has_bitstrings:
                updated_obs = (*emulation_config.observables, BitStrings(num_shots=self._runs))
                emulation_config = emulation_config.with_changes(observables=updated_obs)

        if self._runs is not None:
            emulation_config = emulation_config.with_changes(default_num_shots=self._runs)

        return emulation_config

    def default_emulation_config(self) -> EmulationConfig:
        """Return a unique emulation config for all emulators.

        Defaults to a configuration that asks for the final bitstring, sampled `runs` times.
        """
        return EmulationConfig(observables=(BitStrings(num_shots=self._runs),))


class PulserRemoteBackend:

    @staticmethod
    def validate_connection(connection: RemoteConnection) -> RemoteConnection:
        """Validate the required connection to instantiate a RemoteBackend.

        Remote emulators and QPUs require a `pulser.backend.remote.RemoteConnection` or derived
        to send jobs. Validation also happens inside the backend. Early validation just makes the
        error easier to understand.
        """
        if not isinstance(connection, RemoteConnection):
            raise TypeError(f"""Error in `PulserRemoteBackend`:
                `connection` must be of type {RemoteConnection}.""")
        return connection


class LocalEmulator(PulserEmulatorBackend):
    """
    Run QoolQit `QuantumProgram`s on a Pasqal local emulator backends.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and local emulator backends.

    Args:
        backend_type (type): backend type. Must be a subtype of `pulser.backend.EmulatorBackend`.
        emulation_config (EmulationConfig): optional configuration object emulators.
        runs (int): number of bitstring samples to collect from the final quantum state.

    Examples:
        ```python
        from qoolqit.execution import LocalEmulator, BackendType
        backend = LocalEmulator(backend_type=BackendType.QutipBackendV2)
        result = backend.run(program)
        ```
    """

    def __init__(
        self,
        *,
        backend_type: type[EmulatorBackend] = QutipBackendV2,
        emulation_config: EmulationConfig | None = None,
        runs: int | None = None,
    ) -> None:
        """Instantiates a LocalEmulator."""
        super().__init__(runs=runs)
        if not issubclass(backend_type, EmulatorBackend):
            raise TypeError(
                "Error in `LocalEmulator`: `backend_type` must be a EmulatorBackend type."
            )
        self._backend_type = backend_type
        self._emulation_config = self.validate_emulation_config(emulation_config)

    def run(self, program: QuantumProgram) -> Sequence[Results]:
        """Run a compiled QuantumProgram and return the results."""
        self._backend = self._backend_type(program.compiled_sequence, config=self._emulation_config)
        results = self._backend.run()
        res_seq = (results,) if isinstance(results, Results) else tuple(results)
        return res_seq


class RemoteEmulator(PulserEmulatorBackend, PulserRemoteBackend):
    """
    Run QoolQit `QuantumProgram`s on a Pasqal remote emulator backends.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and remote emulator backends.
    The behavior is similar to `LocalEmulator`, but here, requires credentials through
    a `connection` to submit/run a program.
    To get your credentials and to create a connection object, please refer to the [Pasqal Cloud
    interface documentation](https://docs.pasqal.com/cloud).

    Args:
        backend_type (type): backend type. Must be a subtype of
            `pulser_pasqal.backends.RemoteEmulatorBackend`.
        connection (RemoteConnection): connection to execute the program on remote backends.
        emulation_config (EmulationConfig): optional configuration object emulators.
        runs (int): number of bitstring samples to collect from the final quantum state.

    Examples:
        ```python
        from pulser_pasqal import PasqalCloud
        from qoolqit.execution import RemoteEmulator, BackendType
        connection = PasqalCloud(username=..., password=..., project_id=...)
        backend = RemoteEmulator(backend_type=BackendType.EmuFreeBackendV2, connection=connection)
        ```
        then
        ```python
        remote_results = backend.submit(program)
        ```
        or
        ```python
        results = backend.run(program)
        ```
    """

    def __init__(
        self,
        *,
        backend_type: type[RemoteEmulatorBackend] = EmuFreeBackendV2,
        connection: RemoteConnection,
        emulation_config: EmulationConfig | None = None,
        runs: int | None = None,
    ) -> None:
        """Instantiates a RemoteEmulator."""
        super().__init__(runs=runs)
        if not issubclass(backend_type, RemoteEmulatorBackend):
            raise TypeError(
                "Error in `RemoteEmulator`: `backend_type` must be a RemoteEmulatorBackend type."
            )
        self._backend_type = backend_type
        self._connection = self.validate_connection(connection)
        self._emulation_config = self.validate_emulation_config(emulation_config)

    def submit(self, program: QuantumProgram, wait: bool = False) -> RemoteResults:
        """Submit a compiled QuantumProgram and return a remote handler of the results.

        The returned handler `RemoteResults` can be used to:
        - query the job status with `remote_results.get_batch_status()`
        - when DONE, retrieve results with `remote_results.results`

        Args:
            program (QuantumProgram): the compiled quantum program to run.
            wait (bool): Wait for remote backend to complete the job.
        """
        # Instantiate backend
        self._backend = self._backend_type(
            program.compiled_sequence,
            connection=self._connection,
            config=self._emulation_config,
        )
        remote_results = self._backend.run(wait=wait)
        return remote_results

    def run(self, program: QuantumProgram) -> Sequence[Results]:
        """Run a compiled QuantumProgram remotely and return the results."""
        remote_results = self.submit(program, wait=True)
        res_seq: Sequence[Results] = remote_results.results
        return res_seq


class QPU(PulserRemoteBackend):
    """Execute QoolQit QuantumPrograms on Pasqal quantum processing units.

    This class provides the primary interface for running quantum programs on actual
    QPU hardware. It requires authenticated credentials through a connection object
    to submit and execute programs on remote quantum processors.

    Args:
        connection: Authenticated connection to the remote QPU backend.
        runs: Number of bitstring samples to collect from the final quantum state.

    Examples:
        Using Pasqal Cloud:
        ```python
        from pulser_pasqal import PasqalCloud
        from qoolqit.execution import QPU

        connection = PasqalCloud(
            username="your_username",
            password="your_password",
            project_id="your_project_id"
        )
        backend = QPU(connection=connection)
        remote_results = backend.submit(program)
        ```

        Using Atos MyQML:
        ```python
        from pulser_myqlm import PulserQLMConnection
        from qoolqit.execution import QPU

        connection = PulserQLMConnection()
        backend = QPU(connection=connection)
        results = backend.run(program)
        ```

    Note:
        Contact your quantum computing provider for credentials and connection setup:
        - [Pasqal Cloud Documentation](https://docs.pasqal.com/cloud)
        - [Atos MyQML Framework](https://github.com/pasqal-io/Pulser-myQLM)
    """

    def __init__(
        self,
        *,
        connection: RemoteConnection,
        runs: int | None = None,
    ) -> None:
        """Instantiates a QPU backend."""
        self._backend_type = QPUBackend
        self._connection = self.validate_connection(connection)
        if runs is None:
            raise ValueError(
                """Number of runs must be provided to use the QPU backend.
                Please specify the number of runs when creating the QPU instance.
                For example: QPU(connection=..., runs=100)""",
            )
        self._config = BackendConfig(default_num_shots=runs)

    def submit(self, program: QuantumProgram, wait: bool = False) -> RemoteResults:
        """Submit a compiled quantum program to the QPU and return a result handler.

        Args:
            program: The compiled quantum program to execute on the QPU.
            wait: Whether to wait for the QPU to complete execution before returning.

        Returns:
            A remote result handler for monitoring job status and retrieving results.

        Note:
            The returned RemoteResults object provides:
            - Job status monitoring via `get_batch_status()`
            - Result retrieval via the `results` property (when job is complete)
        """
        self._backend = self._backend_type(
            program.compiled_sequence, connection=self._connection, config=self._config
        )
        remote_results = self._backend.run(wait=wait)
        return remote_results

    def run(self, program: QuantumProgram) -> Sequence[Results]:
        """Execute a compiled quantum program on the QPU and return the results.

        This method submits the program and waits for completion before returning
        the final results.

        Args:
            program: The compiled quantum program to execute on the QPU.

        Returns:
            The execution results from the QPU.
        """
        remote_results = self.submit(program, wait=True)
        res_seq: Sequence[Results] = remote_results.results
        return res_seq
