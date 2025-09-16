from __future__ import annotations

import logging
from collections.abc import Sequence

from pulser.backend import Backend, BitStrings, Results
from pulser.backend.abc import EmulatorBackend
from pulser.backend.config import EmulationConfig
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import JobParams, RemoteBackend, RemoteConnection
from pulser.sequence import Sequence as PulserSequence
from pulser_pasqal.backends import RemoteEmulatorBackend
from pulser_pasqal.pasqal_cloud import PasqalCloud
from pulser_simulation import QutipBackendV2


class PulserBackend:
    """
    Class to run a QoolQit `QuantumProgram` on multiple Pasqal's backends.

    This class serves as a primary interface between tools written using Qoolqit (including solvers)
    and Pasqal's backends (including QPUs and local/remote emulators).

    Args:
        backend_type (type): backend type from PulserBackend.available_backends().
        emulator_config (EmulationConfig): optional configuration object emulators.
            This argument is used only if `backend_type` is an emulator backend.
        connection (RemoteConnection): connection to execute the program on remote backends.
            This argument is used only if `backend_type` is a remote backend.
        runs (int):

    Examples:
        TODO:
         - local and remote example
         - links to documentation
    """

    # default emulator configuration to return final time bitstrings
    default_config = EmulationConfig(
        observables=(BitStrings(num_shots=100),), log_level=logging.WARN
    )

    def __init__(
        self,
        *,
        backend_type: type[Backend] = QutipBackendV2,
        emulation_config: EmulationConfig | None = None,
        connection: RemoteConnection | None = None,
        runs: int = 100,  # is 100 fine?
    ) -> None:

        self._backend_type: type[Backend] = self.validate_backend_type(backend_type)
        if issubclass(self._backend_type, RemoteBackend):
            self._connection: RemoteConnection = self.validate_connection(connection)
        self._emulation_config = emulation_config if emulation_config else self.default_config
        self._runs = runs

    @staticmethod
    def validate_backend_type(backend_type: type[Backend]) -> type[Backend]:
        """Validate backend type."""
        # only support backends based on pulser.backend.Backend
        # checking early otherwise the contructor backend_type(sequence) will fail.
        if not issubclass(backend_type, Backend):
            raise TypeError(f"{backend_type.__name__} is not a supported backend type.")
        return backend_type

    def validate_connection(self, connection: RemoteConnection | None) -> RemoteConnection:
        """Validate the required PasqalCloud connection for remote backends.

        Note:
            Local emulators and internal QPUs require a `PasqalCloud` connection to send jobs.
            Client's QPUs require a derived OVHConnection(PasqalCloud).
        """
        if not isinstance(connection, RemoteConnection):
            raise TypeError(
                f"""Error in `PulserBackend`: a remote backend of type
                {self._backend_type.__name__} requires a `connection` of type {RemoteConnection}."""
            )
        if issubclass(self._backend_type, RemoteEmulatorBackend):
            if not isinstance(connection, PasqalCloud):
                raise TypeError(
                    f"""Error in `PulserBackend`: a remote backend of type
                    {self._backend_type.__name__} requires a `connection` of type {PasqalCloud}."""
                )

        return connection

    def run(self, sequence: PulserSequence) -> Results | Sequence[Results]:
        """Run a QuantumProgram and return the results.

        Note:
            For simplicity let's just focus on running a Sequence now.
            A QuantumProgram will simply host a compiled sequence internally.
        """
        if issubclass(self._backend_type, RemoteBackend):
            if issubclass(self._backend_type, RemoteEmulatorBackend):
                backend = self._backend_type(
                    sequence=sequence, connection=self._connection, config=self._emulation_config
                )
            elif issubclass(self._backend_type, QPUBackend):
                backend = self._backend_type(sequence=sequence, connection=self._connection)
            else:
                raise TypeError(
                    f"""Error in `PulserBackend`: remote backend of
                    type {self._backend_type.__name__} is not supported"""
                )

            # job_params runs is ignored in emulators
            # TODO: after pulser 1.6 assess if job_params is still needed
            job_params = [JobParams(runs=self._runs)]
            job = backend.run(job_params=job_params, wait=True)
            # job.results returns tuple[Results]
            return job.results[0]

        elif issubclass(self._backend_type, EmulatorBackend):
            backend = self._backend_type(sequence=sequence, config=self._emulation_config)
            return backend.run()
        else:
            raise TypeError(
                f"""Error in `PulserBackend`: backend of type {self._backend_type.__name__}
                is currently not supported."""
            )
