from __future__ import annotations

from collections.abc import Sequence

from pulser.backend import Backend, BitStrings, Results
from pulser.backend.abc import EmulatorBackend
from pulser.backend.config import EmulationConfig
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import RemoteBackend, RemoteConnection, RemoteResults
from pulser.backends import _BACKENDS
from pulser.sequence import Sequence as PulserSequence
from pulser_pasqal.backends import PasqalEmulator
from pulser_pasqal.pasqal_cloud import PasqalCloud
from pulser_simulation import QutipBackendV2


class PulserBackend:
    """
    Class to run Sequence/QuantumProgram on multiple backends.

    This class serves as a primary interface between tools written using Qoolqit (including solvers)
    and backends (including QPUs and emulators).

    Args:
        backend_type: backend type from PulserBackend.available_backends().
        emulator_config:
        connection: connection to execute the program on remote backends.

    Examples:
        TODO:
         - local and remote example
         - links to documentation
    """

    default_config = EmulationConfig(observables=(BitStrings(),), log_level=2000)

    def __init__(
        self,
        *,
        backend_type: type[Backend] = QutipBackendV2,
        emulation_config: EmulationConfig = default_config,
        connection: RemoteConnection | None = None,
    ) -> None:
        # fail immediately if not supported
        if not issubclass(backend_type, (EmulatorBackend, RemoteBackend, QPUBackend)):
            raise TypeError(f"{backend_type.__name__} is not a supported backend type.")

        self.backend_type: type[Backend] = backend_type
        self.emulation_config: EmulationConfig = emulation_config
        self.connection: RemoteConnection | None = connection  # is PasqalCloud sufficient here?

    @staticmethod
    def available_backends() -> None:
        # list will be updated on pulser 1.6
        # would be nice to print them separately as local, remote, QPU, etc.
        print(*_BACKENDS.keys())

    def run(
        self, sequence: PulserSequence
    ) -> Results | Sequence[Results] | RemoteResults | Sequence[RemoteResults]:
        """Run a Sequence/QuantumProgram and return the results.

        Note:
            For simplicity let's just focus on running a Sequence now.
            A QuantumProgram will simply host a compiled sequence internally.
        """

        if issubclass(self.backend_type, EmulatorBackend):
            backend = self.backend_type(sequence=sequence, config=self.emulation_config)
            return backend.run()
        elif issubclass(self.backend_type, PasqalEmulator):
            if not isinstance(self.connection, PasqalCloud):
                raise TypeError(
                    f"""Error in `BackendConfig`: a backend of type {self.backend_type.__name__}
                    requires a `connection` of type {PasqalCloud}."""
                )
            backend = self.backend_type(
                sequence=sequence,
                connection=self.connection,
                config=self.emulation_config,
                mimic_qpu=False,
            )
            return backend.run(wait=True)
        elif issubclass(self.backend_type, QPUBackend):
            if not isinstance(self.connection, RemoteConnection):
                raise TypeError(
                    f"""Error in `BackendConfig`: a backend of type {self.backend_type.__name__}
                    requires a `connection` of type {RemoteConnection}."""
                )
            backend = self.backend_type(sequence=sequence, connection=self.connection)
            return backend.run()
        else:
            raise TypeError(
                f"""Error in `BackendConfig`: backends of type {self.backend_type.__name__}
                is currently not supported."""
            )
