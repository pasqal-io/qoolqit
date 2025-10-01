from __future__ import annotations

from collections.abc import Sequence
from typing import Optional

from pulser.backend import BitStrings, Results
from pulser.backend.abc import EmulatorBackend
from pulser.backend.config import EmulationConfig
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import JobParams, RemoteConnection, RemoteResults
from pulser_pasqal.backends import EmuFreeBackendV2, RemoteEmulatorBackend
from pulser_simulation import QutipBackendV2

from qoolqit.program import QuantumProgram


class PulserEmulatorBackend:
    _runs: int

    def validate_emulation_config(
        self, emulation_config: Optional[EmulationConfig]
    ) -> EmulationConfig:
        """Returns a valid config for emulator backends, if needed.

        Args:
            emulation_config (EmulationConfig): base configuration class for all emulators backends.
                If no config is provided to an emulator backend, a default will be provided instead.
        Note:
            Emulators backend (local/remote) can be configured through the generic
            `EmulationConfig` object. Early validation makes the error easier to understand.
        """
        if emulation_config is None:
            emulation_config = self.default_emulation_config()
            # TODO: validate config when bump to pulser==1.6 (uncomment below)
            # config = backend_type.validate_config(config)
        return emulation_config

    def default_emulation_config(self) -> EmulationConfig:
        """Return a default and unique emulation config for all emulators.

        Note:
            If `emulation_config` not specified in `PulserBackend`, to provide a
            consistent experience between emulators, we set default configuration that
            asks for the final bitstring, sampled `runs` times.
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
            raise TypeError(
                f"""Error in `PulserRemoteBackend`:
                `connection` must be of type {RemoteConnection}."""
            )
        return connection


class Emulator(PulserEmulatorBackend):
    """
    Run QoolQit `QuantumProgram`s on a Pasqal local backend.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and Pasqal backends local emulators backends.

    Args:
        backend_type (type): backend type. Must be a subtype of pulser.backend.Backend.
        emulator_config (EmulationConfig): optional configuration object emulators.
            This argument is used only if `backend_type` is an emulator backend.
        runs (int): run the program `runs` times to collect bitstrings statistics.
            On QPU backends this represents the actual number of runs of the program.
            On emulators, instead the bitstring are sampled from the quantum state `runs` times.

    Examples:
        ```python
        from qoolqit import PulserBackend, SVBackend
        backend = PulserBackend(backend_type=SVBackend)
        result = backend.run(program)
        ```
    """

    def __init__(
        self,
        *,
        backend_type: type[EmulatorBackend] = QutipBackendV2,
        emulation_config: Optional[EmulationConfig] = None,
        runs: int = 100,
    ) -> None:
        if not issubclass(backend_type, EmulatorBackend):
            raise TypeError("Error in `Emulator`: `backend_type` must be a EmulatorBackend type.")
        self._backend_type = backend_type
        self._runs = runs
        self._emulation_config = self.validate_emulation_config(emulation_config)

    def run(self, program: QuantumProgram) -> Results | Sequence[Results]:
        """Run a compiled QuantumProgram and return the results."""
        self._backend = self._backend_type(program.compiled_sequence, config=self._emulation_config)
        result = self._backend.run()
        return result


class RemoteEmulator(PulserEmulatorBackend, PulserRemoteBackend):
    """
    Run QoolQit `QuantumProgram`s on a Pasqal remote backend.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and Pasqal remote emulators backends, including QPUs, digital-twins and remote emulators.
    The behvior is similar to the local `Emulator` class, but here, requires credentials
    through a `connection` to run a program.
    To get your credentials and to create a connection object, please refer to the [Pasqal Cloud
    interface documentation](https://docs.pasqal.com/cloud).

    Args:
        backend_type (type): backend type. Must be a subtype of pulser.backend.Backend.
        connection (RemoteConnection): connection to execute the program on remote backends.
        emulator_config (EmulationConfig): optional configuration object emulators.
            This argument is used only if `backend_type` is an emulator backend.
        runs (int): run the program `runs` times to collect bitstrings statistics.
            On QPU backends this represents the actual number of runs of the program.
            On emulators, instead the bitstring are sampled from the quantum state `runs` times.

    Examples:
        ```python
        from pulser_pasqal import PasqalCloud
        from qoolqit import PulserRemoteBackend, EmuFreeBackendV2
        connection = PasqalCloud(username=..., password=..., project_id=...)
        backend = PulserRemoteBackend(backend_type=EmuFreeBackendV2, connection=connection)
        ```
        then
        ```python
        remote_results = backend.submit(program)
        ```
        or
        ```python
        results = backend.run(program)
    """

    def __init__(
        self,
        *,
        backend_type: type[RemoteEmulatorBackend] = EmuFreeBackendV2,
        connection: RemoteConnection,
        emulation_config: Optional[EmulationConfig] = None,
        runs: int = 100,
    ) -> None:

        if not issubclass(backend_type, RemoteEmulatorBackend):
            raise TypeError(
                "Error in `RemoteEmulator`: `backend_type` must be a RemoteEmulatorBackend type."
            )
        self._backend_type = backend_type
        self._runs = runs
        self._emulation_config = self.validate_emulation_config(emulation_config)
        self._connection = self.validate_connection(connection)

    def submit(self, program: QuantumProgram, wait: bool = False) -> RemoteResults:
        """Submit a compiled QuantumProgram and return a remote handler of the results.

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

        # in QPU backends `runs` is specified in a JobParams object
        # in remote emulators JobParams is ignored and the number
        # of runs required by the user is set instead in `default_emulation_config()`.
        # TODO: after pulser 1.6 assess if job_params is still needed
        job_param = JobParams(runs=self._runs)
        remote_results = self._backend.run(job_params=[job_param], wait=wait)
        return remote_results

    def run(self, program: QuantumProgram) -> Results | Sequence[Results]:
        """Run a compiled QuantumProgram remotely and return the results."""
        remote_results = self.submit(program, wait=True)
        return remote_results.results


class QPU(PulserRemoteBackend):
    """
    Run QoolQit `QuantumProgram`s on a Pasqal QPU.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and Pasqal QPU backend. It requires credentials through a `connection` to submit a program.
    Please, contact your provider to get your credentials and get help on how create a
    connection object:
    - [Pasqal Cloud interface documentation](https://docs.pasqal.com/cloud)
    - [Atos MyQML framework](https://github.com/pasqal-io/Pulser-myQLM/blob/main/tutorials/Submitting%20AFM%20state%20prep%20to%20QPU.ipynb)

    Args:
        backend_type (type): backend type. Must be a subtype of pulser.backend.Backend.
        connection (RemoteConnection): connection to execute the program on remote backends.
        runs (int): run the program `runs` times to collect bitstrings statistics.
            On QPU backends this represents the actual number of runs of the program.
            On emulators, instead the bitstring are sampled from the quantum state `runs` times.

    Examples:
        ```python
        from pulser_pasqal import PasqalCloud
        from qoolqit import PulserQPUBackend
        connection = PasqalCloud(username=..., password=..., project_id=...)
        backend = PulserQPUBackend(connection=connection)
        ```
        then
        ```python
        remote_results = backend.submit(program)
        ```
        or
        ```python
        results = backend.run(program)
    """

    def __init__(
        self,
        *,
        connection: RemoteConnection,
        runs: int = 100,
    ) -> None:

        self._backend_type = QPUBackend
        self._runs = runs
        self._connection = self.validate_connection(connection)

    def submit(self, program: QuantumProgram, wait: bool = False) -> RemoteResults:
        """Submit a compiled QuantumProgram and return a remote handler of the results.

        Args:
            program (QuantumProgram): the compiled quantum program to run.
            wait (bool): Wait for remote backend to complete the job.
        """
        self._backend = self._backend_type(program.compiled_sequence, connection=self._connection)
        job_param = JobParams(runs=self._runs)
        remote_results = self._backend.run(job_params=[job_param], wait=wait)
        return remote_results

    def run(self, program: QuantumProgram) -> Results | Sequence[Results]:
        """Run a compiled QuantumProgram remotely and return the results."""
        remote_results = self.submit(program, wait=True)
        return remote_results.results
