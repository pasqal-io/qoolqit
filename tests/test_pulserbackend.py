from __future__ import annotations

from collections.abc import Sequence
from unittest.mock import MagicMock

import pytest
from pulser.backend import Backend, EmulationConfig, EmulatorBackend, Results
from pulser.backend.remote import JobParams, RemoteBackend, RemoteConnection, RemoteResults
from pulser.sequence import Sequence as PulserSequence

from qoolqit.program import QuantumProgram
from qoolqit.pulserbackend import PulserBackend


class TestPulserBackend:

    mock_connection = MagicMock(spec=RemoteConnection)
    mock_config = MagicMock(spec=EmulationConfig)
    mock_sequence = MagicMock(spec=PulserSequence)
    mock_program_compiled = MagicMock(spec=QuantumProgram, _compiled_sequence=mock_sequence)
    mock_program_not_compiled = MagicMock(spec=QuantumProgram, _compiled_sequence=None)

    class MockBackend(Backend):
        def run(self) -> Results | Sequence[Results]:
            return MagicMock(spec=Results)

    class MockEmulatorBackend(EmulatorBackend):
        default_config = MagicMock(spec=EmulationConfig)

        @staticmethod
        def validate_sequence(sequence: PulserSequence, mimic_qpu: bool = False) -> None:
            pass

        def run(self) -> Results | Sequence[Results]:
            return MagicMock(spec=Results)

    class MockRemoteBackend(RemoteBackend):
        def run(
            self, job_params: list[JobParams] | None = None, wait: bool = False
        ) -> RemoteResults:
            return MagicMock(spec=RemoteResults)

    def test_default_backend(self) -> None:
        backend = PulserBackend(backend_type=self.MockBackend)
        assert backend._backend_type is self.MockBackend
        assert backend._emulation_config is None
        assert backend._runs == 100

    def test_default_remote_backend(self) -> None:
        backend = PulserBackend(
            backend_type=self.MockRemoteBackend, connection=self.mock_connection
        )
        assert backend._backend_type is self.MockRemoteBackend
        assert backend._connection is self.mock_connection
        assert backend._emulation_config is None
        assert backend._runs == 100

    def test_backend_with_config(self) -> None:
        backend = PulserBackend(backend_type=self.MockBackend, emulation_config=self.mock_config)
        assert backend._emulation_config is self.mock_config

    def test_validate_backend_type(self) -> None:
        backend = PulserBackend.validate_backend_type(self.MockBackend)
        assert backend is self.MockBackend

        with pytest.raises(match=f"{int.__name__} is not a supported backend type."):
            PulserBackend.validate_backend_type(int)

    def test_validate_connection(self) -> None:
        backend = PulserBackend(
            backend_type=self.MockRemoteBackend, connection=self.mock_connection
        )
        connection = backend.validate_connection(self.mock_connection)
        assert connection is self.mock_connection

        with pytest.raises(
            match=f"""Error in `PulserBackend`: remote backend type {backend._backend_type.__name__}
                requires a `connection` of type {RemoteConnection}."""
        ):
            backend.validate_connection(4.0)

    def test_default_emulation_config(self) -> None:
        backend = PulserBackend(backend_type=self.MockEmulatorBackend)
        backend.run(self.mock_program_compiled)

        expected_config = backend.default_emulation_config()
        # convert the expected config to a str
        expected_config_repr = expected_config.to_abstract_repr()

        config = backend._emulation_config
        assert isinstance(config, EmulationConfig)
        # convert the saved config to a str
        config_repr = config.to_abstract_repr()

        assert config_repr == expected_config_repr

    def test_not_compiled_seq(self) -> None:
        backend = PulserBackend(backend_type=self.MockEmulatorBackend)
        with pytest.raises(match="QuantumProgram has not been compiled."):
            backend.run(self.mock_program_not_compiled)
