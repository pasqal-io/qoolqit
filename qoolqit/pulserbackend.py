from __future__ import annotations

import logging
import warnings
from collections.abc import Sequence

from pulser.backend import Backend, BitStrings, Results
from pulser.backend.abc import EmulatorBackend
from pulser.backend.config import EmulationConfig
from pulser.backend.remote import JobParams, RemoteBackend, RemoteConnection
from pulser_pasqal.backends import RemoteEmulatorBackend
from pulser_pasqal.pasqal_cloud import PasqalCloud
from pulser_simulation import QutipBackendV2

from qoolqit import QuantumProgram


class PulserBackend:
    """
    Class to run a QoolQit `QuantumProgram` on multiple Pasqal backends.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and Pasqal backends (including QPUs and local/remote emulators).

    Args:
        backend_type (type): backend type. Must be a subtype of pulser.backend.Backend.
        emulator_config (EmulationConfig): optional configuration object emulators.
            This argument is used only if `backend_type` is an emulator backend.
        connection (RemoteConnection): connection to execute the program on remote backends.
            This argument is used only if `backend_type` is a remote backend.
        runs (int): run the program `runs` times to collect bitstrings statistics.
            On QPU backends this represents the actual number of runs of the program.
            On emulators, the quantum state is bitstring sampled `runs` times.

    Notes:
        TODO: links to documentation

    Examples:
        ```python
        from qoolqit import PulserBackend
        from emu_sv import SVBackend
        backend = PulserBackend(backend_type=SVBackend)
        result = backend.run(program)
        ```
    """

    def __init__(
        self,
        *,
        backend_type: type[Backend] = QutipBackendV2,
        connection: RemoteConnection | None = None,
        emulation_config: EmulationConfig | None = None,
        runs: int = 100,
    ) -> None:

        self._backend_type = self.validate_backend_type(backend_type)
        self._runs = runs
        # require a connection for RemoteBackend
        self._connection = self.validate_connection(connection)
        # accept and validate the config for EmulatorBackend
        self._emulation_config = self.validate_emulation_config(emulation_config)

    @staticmethod
    def validate_backend_type(backend_type: type[Backend]) -> type[Backend]:
        """Validate backend type.

        Note:
            Early validation that the provided backend is derived from `pulser.backend.Backend`.
            We re-validate during run() as we dispatch to the proper handlers, but early validation
            makes the error easier to understand.
        """
        if not issubclass(backend_type, Backend):
            raise TypeError(f"{backend_type.__name__} is not a supported backend type.")
        return backend_type

    def validate_connection(self, connection: RemoteConnection | None) -> RemoteConnection | None:
        """Validate the required connection for remote backends.

        Note:
            Remote emulators and QPUs require a `pulser.backend.remote.RemoteConnection`
            or derived to send jobs. Early validation makes the error easier to understand.
        """
        if issubclass(self._backend_type, RemoteBackend):
            if not isinstance(connection, RemoteConnection):
                raise TypeError(
                    f"""Error in `PulserBackend`: remote backend type {self._backend_type.__name__}
                    requires a `connection` of type {RemoteConnection}."""
                )
            if issubclass(self._backend_type, RemoteEmulatorBackend):
                if not isinstance(connection, PasqalCloud):
                    raise TypeError(
                        f"""Error in `PulserBackend`: remote backend type
                        {self._backend_type.__name__} requires a `connection`
                        of type {PasqalCloud}."""
                    )
        elif connection:
            warnings.warn(
                f"""Warning in `PulserBackend`: a `connection` has been passed to the
                local backend {self._backend_type.__name__} which does not require it.
                It will be ignored."""
            )
            connection = None

        return connection

    def validate_emulation_config(
        self, emulation_config: EmulationConfig | None
    ) -> EmulationConfig | None:
        """Returns a valid config for emulator backends, if needed.

        Args:
            emulation_config (EmulationConfig): base configuration class for all emulators backends.
                If no config is provided to an emulator backend, a default will be provided instead.
        Note:
            Emulators backend (local/remote) can be configured through the generic
            `EmulationConfig` object. Early validation makes the error easier to understand.
        """
        if issubclass(self._backend_type, EmulatorBackend):
            if emulation_config is None:
                emulation_config = self.default_emulation_config()
                # TODO: validate config when pulser 1.6 is released (uncomment below)
                # config = self._backend_type.validate_config(config)
        elif emulation_config:
            warnings.warn(
                f"""Warning in `PulserBackend`: an `emulation_config` has been passed to the
                a non-emulator backend {self._backend_type.__name__} which does not require it.
                It will be ignored."""
            )
        return emulation_config

    def default_emulation_config(self) -> EmulationConfig:
        """Return a default and unique emulation config for all emulators.

        Note:
            If `emulation_config` not specified in `PulserBackend`, to provide a
            consistent experience between emulators, we set default configuration that
            asks for the final bitstring, sampled `runs` times.
        """
        # log_level set to WARN to remove unwanted INFO output from emulators
        return EmulationConfig(
            observables=(BitStrings(num_shots=self._runs),), log_level=logging.WARN
        )

    def run(self, program: QuantumProgram) -> Results | Sequence[Results]:
        """Run a compiled QuantumProgram and return the results."""
        if program._compiled_sequence is None:
            raise ValueError(
                "QuantumProgram has not been compiled. Please call program.compile_to(device)."
            )
        # Instantiate internal backend
        backend_kwargs = {"mimic_qpu": False}
        if self._connection:
            backend_kwargs["connection"] = self._connection
        if self._emulation_config:
            backend_kwargs["config"] = self._emulation_config

        self._backend = self._backend_type(program.compiled_sequence, **backend_kwargs)

        if self._connection:
            # job_params `runs` is used in QPUBackend but ignored in remote emulators
            # since it is specified in the emulation config
            # TODO: after pulser 1.6 assess if job_params is still needed
            job_params = [JobParams(runs=self._runs)]
            job = self._backend.run(job_params=job_params, wait=True)
            # len(job.results) == len(job_params) == 1
            results = job.results[0]
            return results
        else:
            return self._backend.run()
