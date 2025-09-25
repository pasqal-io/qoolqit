from __future__ import annotations

import warnings
from collections.abc import Sequence
from typing import Optional

from pulser.backend import Backend, BitStrings, Results
from pulser.backend.abc import EmulatorBackend
from pulser.backend.config import EmulationConfig
from pulser.backend.remote import JobParams, RemoteBackend, RemoteConnection, RemoteResults
from pulser_pasqal.backends import EmuFreeBackendV2
from pulser_simulation import QutipBackendV2

from qoolqit import QuantumProgram


class BasePulserBackend:
    _runs: int

    def validate_emulation_config(
        self, backend_type: type[Backend], emulation_config: Optional[EmulationConfig]
    ) -> Optional[EmulationConfig]:
        """Returns a valid config for emulator backends, if needed.

        Args:
            emulation_config (EmulationConfig): base configuration class for all emulators backends.
                If no config is provided to an emulator backend, a default will be provided instead.
        Note:
            Emulators backend (local/remote) can be configured through the generic
            `EmulationConfig` object. Early validation makes the error easier to understand.
        """
        if issubclass(backend_type, EmulatorBackend):
            if emulation_config is None:
                emulation_config = self.default_emulation_config()
                # TODO: validate config when pulser 1.6 is released (uncomment below)
                # config = backend_type.validate_config(config)
        elif emulation_config:
            warnings.warn(
                f"""Warning in `PulserBackend`: an `emulation_config` has been passed to the
                a non-emulator backend {backend_type.__name__} which does not require it.
                It will be ignored."""
            )
            emulation_config = None
        return emulation_config

    def default_emulation_config(self) -> EmulationConfig:
        """Return a default and unique emulation config for all emulators.

        Note:
            If `emulation_config` not specified in `PulserBackend`, to provide a
            consistent experience between emulators, we set default configuration that
            asks for the final bitstring, sampled `runs` times.
        """
        # log_level set to WARN to remove unwanted INFO output from emulators
        return EmulationConfig(observables=(BitStrings(num_shots=self._runs),))


class PulserBackend(BasePulserBackend):
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
            raise TypeError(
                """Error in `PulserBackend`: `backend_type` must be a EmulatorBackend type."""
            )
        self._backend_type = backend_type
        self._runs = runs
        self._emulation_config = self.validate_emulation_config(
            self._backend_type, emulation_config
        )

    def run(self, program: QuantumProgram) -> Results | Sequence[Results]:
        """Run a compiled QuantumProgram and return the results."""
        if program._compiled_sequence is None:
            raise ValueError(
                "QuantumProgram has not been compiled. Please call program.compile_to(device)."
            )
        # Instantiate backend
        self._backend = self._backend_type(program.compiled_sequence, config=self._emulation_config)

        result = self._backend.run()
        return result


class PulserRemoteBackend(BasePulserBackend):
    """
    Run QoolQit `QuantumProgram`s on a Pasqal remote backend.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and Pasqal remote backends, including QPUs, digital-twins and remote emulators.
    The behvior is similar to the local PulserBackend class, but here, requires credentials
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
        backend_type: type[RemoteBackend] = EmuFreeBackendV2,
        connection: RemoteConnection,
        emulation_config: Optional[EmulationConfig] = None,
        runs: int = 100,
    ) -> None:

        if not issubclass(backend_type, RemoteBackend):
            raise TypeError(
                """Error in `PulserRemoteBackend`: `backend_type` must be a RemoteBackend type."""
            )
        self._backend_type = backend_type
        self._runs = runs
        self._emulation_config = self.validate_emulation_config(
            self._backend_type, emulation_config
        )
        # require a connection for RemoteBackend
        self._connection = self.validate_connection(connection)

    def validate_connection(self, connection: RemoteConnection) -> RemoteConnection:
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

    def submit(self, program: QuantumProgram, wait: bool = False) -> RemoteResults:
        """Run a compiled QuantumProgram and return a remote handler of the results.

        Args:
            program (QuantumProgram): the compiled quantum program to run.
            wait (bool): Wait for remote backend to complete the job.
        """
        if program._compiled_sequence is None:
            raise ValueError(
                "QuantumProgram has not been compiled. Please call program.compile_to(device)."
            )

        # Instantiate backend
        if self._emulation_config:
            self._backend = self._backend_type(
                program.compiled_sequence,
                connection=self._connection,
                config=self._emulation_config,
            )
        else:  # is QPU
            self._backend = self._backend_type(
                program.compiled_sequence, connection=self._connection
            )

        # in QPU backends `runs` is specified in a JobParams object
        # in remote emulators JobParams is ignored and the number
        # of runs required by the user is set instead in `default_emulation_config()`.
        # TODO: after pulser 1.6 assess if job_params is still needed
        job_param = JobParams(runs=self._runs)
        remote_results = self._backend.run(job_params=[job_param], wait=wait)
        return remote_results

    def run(self, program: QuantumProgram) -> Results | Sequence[Results]:
        """Run a compiled QuantumProgram and return the results."""
        remote_results = self.submit(program, wait=True)
        return remote_results.results
