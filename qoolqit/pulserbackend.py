from __future__ import annotations

import logging
from collections.abc import Sequence

from pulser.backend import Backend, BitStrings, Results
from pulser.backend.abc import EmulatorBackend
from pulser.backend.config import EmulationConfig
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import JobParams, RemoteBackend
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
        emulator_config (EmulationConfig): optional configuration object to configure
            remote and local emulators.
        connection (RemoteConnection): connection to execute the program on remote backends.
        mimic_qpu (bool):  Whether to mimic the validations necessary for
            execution on a QPU.

    Examples:
        TODO:
         - local and remote example
         - links to documentation
    """

    # default emulator configuration to return final time bitstrings
    default_config = EmulationConfig(observables=(BitStrings(),), log_level=logging.WARN)

    def __init__(
        self,
        *,
        backend_type: type[Backend] = QutipBackendV2,
        emulation_config: EmulationConfig | None = None,
        connection: PasqalCloud | None = None,
        mimic_qpu: bool = False,
    ) -> None:

        self.backend_type: type[Backend] = self.validate_backend_type(backend_type)
        if issubclass(self.backend_type, RemoteBackend):
            self.connection: PasqalCloud = self.validate_connection(connection)
        self.emulation_config = emulation_config if emulation_config else self.default_config
        self.mimic_qpu: bool = mimic_qpu

    @staticmethod
    def validate_backend_type(backend_type: type[Backend]) -> type[Backend]:
        """Only suppport Pulser EmulatorBackend or RemoteBackend subclasses backend type."""
        if not issubclass(backend_type, (EmulatorBackend, RemoteBackend)):
            raise TypeError(f"{backend_type.__name__} is not a supported backend type.")
        return backend_type

    def validate_connection(self, connection: PasqalCloud | None) -> PasqalCloud:
        """Validate the required PasqalCloud connection for remote backends.

        Note:
            Local emulators and internal QPUs require a `PasqalCloud` connection to send jobs.
            Client's QPUs require a derived OVHConnection(PasqalCloud).
        """
        if not isinstance(connection, PasqalCloud):
            raise TypeError(
                f"""Error in `PulserBackend`: a remote backend of type {self.backend_type.__name__}
                requires a `connection` of type {PasqalCloud}."""
            )
        return connection

    def run(self, sequence: PulserSequence) -> Results | Sequence[Results]:
        """Run a QuantumProgram and return the results.

        Note:
            For simplicity let's just focus on running a Sequence now.
            A QuantumProgram will simply host a compiled sequence internally.
        """
        if issubclass(self.backend_type, RemoteBackend):
            if issubclass(self.backend_type, RemoteEmulatorBackend):
                backend = self.backend_type(
                    sequence=sequence,
                    connection=self.connection,
                    config=self.emulation_config,
                    mimic_qpu=self.mimic_qpu,
                )
            elif issubclass(self.backend_type, QPUBackend):
                backend = self.backend_type(sequence=sequence, connection=self.connection)
            else:
                raise TypeError(
                    f"""Error in `PulserBackend`: remote backend of
                    type {self.backend_type.__name__} is not supported"""
                )

            # RemoteBackend.run() returns a RemoteResults
            # job_params is ignored in remote_emulators
            # TODO: after pulser 1.6 assess if job_params is still needed
            job = backend.run(job_params=[JobParams(runs=1)], wait=True)
            # job.results returns tuple[Results]
            return job.results[0]

        elif issubclass(self.backend_type, EmulatorBackend):
            backend = self.backend_type(
                sequence=sequence, config=self.emulation_config, mimic_qpu=self.mimic_qpu
            )
            return backend.run()
        else:
            raise TypeError(
                f"""Error in `PulserBackend`: backend of type {self.backend_type.__name__}
                is currently not supported."""
            )
