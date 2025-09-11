# import pulser.backends as backends
from __future__ import annotations

from pulser.backend import Backend, EmulationConfig, EmulatorBackend, Results
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import RemoteBackend, RemoteResults
from pulser_pasqal import PasqalCloud
from pulser_simulation import QutipBackendV2

from qoolqit import QuantumProgram


class PulserBackend:
    """Class to run Sequence/Quantum program on multiple backends."""

    def __init__(
        self,
        program: QuantumProgram,
        backend_type: type[Backend] = QutipBackendV2,
        backend_config: EmulationConfig | None = None,
        connection: PasqalCloud | None = None,
    ):
        if issubclass(backend_type, EmulatorBackend):
            pass
        elif issubclass(backend_type, RemoteBackend):
            pass
        elif issubclass(backend_type, QPUBackend):
            pass
        else:
            raise TypeError(f"{backend_type.__name__} is not a valid backend.")

        self.program = program
        self.backend_type = backend_type
        self.backend_config = backend_config
        self.connection = connection

    def run(self) -> Results | RemoteResults:
        """Run a QuantumProgram and return the results."""

        compiled_seq = self.program._compiled_sequence

        if issubclass(self.backend_type, EmulatorBackend):
            backend = self.backend_type(compiled_seq, config=self.backend_config)
            return backend.run()
        elif issubclass(self.backend_type, RemoteBackend):
            backend = self.backend_type(
                compiled_seq, connection=self.connection, config=self.backend_config
            )
            # RemoteBackend requires kwarg `job_params` which is then ignored
            return backend.run(job_params=[{"nruns": 100}], wait=True)
        elif issubclass(self.backend_type, QPUBackend):
            backend = self.backend_type(compiled_seq, connection=self.connection)
            return backend.run()
        else:
            return None
