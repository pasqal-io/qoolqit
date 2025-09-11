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
        backend_config:
        connection: connection to execute the program on remote backends.

    Examples:
        TODO:
         - local and remote example
         - links to documentation
    """

    default_config = EmulationConfig(observables=(BitStrings(),))

    def __init__(
        self,
        backend_type: type[Backend] = QutipBackendV2,
        backend_config: EmulationConfig = default_config,
        connection: RemoteConnection | None = None,
    ) -> None:
        if not issubclass(backend_type, (EmulatorBackend, RemoteBackend, QPUBackend)):
            raise TypeError(f"{backend_type.__name__} is not a supported backend type.")

        self.backend_type: type[Backend] = backend_type
        self.backend_config: EmulationConfig = backend_config
        self.connection: RemoteConnection | None = connection  # is PasqalCloud sufficient here?

    def available_backends(self) -> None:
        # list will be updated on pulser 1.6
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
            backend = self.backend_type(sequence=sequence, config=self.backend_config)
            return backend.run()
        elif issubclass(self.backend_type, PasqalEmulator):
            if not isinstance(self.connection, PasqalCloud):
                raise TypeError(
                    "Remote execution requires a"
                    "`pulser_pasqal.pasqal_cloud.PasqalCloud` connection."
                )
            backend = self.backend_type(
                sequence=sequence,
                connection=self.connection,
                config=self.backend_config,
                mimic_qpu=False,
            )
            return backend.run(wait=True)
        elif issubclass(self.backend_type, QPUBackend):
            if not isinstance(self.connection, RemoteConnection):
                raise TypeError("Must provide connection.")
            backend = self.backend_type(sequence=sequence, connection=self.connection)
            return backend.run()
        else:
            raise TypeError("Not supported backend.")
