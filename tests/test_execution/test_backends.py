from __future__ import annotations

import json
from collections.abc import Sequence
from unittest.mock import MagicMock

import pytest
from pulser.backend import BitStrings, EmulationConfig, EmulatorBackend, Results
from pulser.backend.config import BackendConfig
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import JobParams, RemoteConnection, RemoteResults
from pulser.sequence import Sequence as PulserSequence
from pulser_pasqal.backends import RemoteEmulatorBackend

from qoolqit.execution import QPU, LocalEmulator, RemoteEmulator
from qoolqit.program import QuantumProgram


class TestBackends:

    mock_connection = MagicMock(spec=RemoteConnection)
    mock_config = MagicMock(spec=EmulationConfig)
    mock_sequence = MagicMock(spec=PulserSequence)
    mock_program_compiled = MagicMock(spec=QuantumProgram, _compiled_sequence=mock_sequence)
    mock_program_not_compiled = MagicMock(
        spec=QuantumProgram, _compiled_sequence=None, is_compiled=False
    )

    class MockEmulatorBackend(EmulatorBackend):
        run_calls = 0
        default_config = MagicMock(spec=EmulationConfig, _backend_options={})

        @staticmethod
        def validate_sequence(sequence: PulserSequence, mimic_qpu: bool = False) -> None:
            pass

        def run(self) -> Results | Sequence[Results]:
            self.run_calls += 1
            return MagicMock(spec=Results)

    class MockRemoteEmulatorBackend(RemoteEmulatorBackend):
        run_calls = 0
        default_config = MagicMock(spec=EmulationConfig, _backend_options={})

        @staticmethod
        def validate_sequence(sequence: PulserSequence, mimic_qpu: bool = False) -> None:
            pass

        def run(
            self, job_params: list[JobParams] | None = None, wait: bool = False
        ) -> RemoteResults:
            self.run_calls += 1
            return MagicMock(spec=RemoteResults)

    def test_default_backend(self) -> None:
        backend = LocalEmulator(backend_type=self.MockEmulatorBackend)
        assert backend._backend_type is self.MockEmulatorBackend
        assert backend._runs is None

    def test_default_remote_backend(self) -> None:
        backend = RemoteEmulator(
            backend_type=self.MockRemoteEmulatorBackend, connection=self.mock_connection
        )
        assert backend._backend_type is self.MockRemoteEmulatorBackend
        assert backend._connection is self.mock_connection
        assert backend._runs is None

    def test_emulator_backend_with_config(self) -> None:
        config = EmulationConfig(observables=(BitStrings(num_shots=1117),))
        backend = LocalEmulator(backend_type=self.MockEmulatorBackend, emulation_config=config)

        # convert configs to str
        expected_config_repr = config.to_abstract_repr()
        config_repr = backend._emulation_config.to_abstract_repr()
        assert config_repr == expected_config_repr

    def test_emulator_backend_with_nruns(self) -> None:
        backend = LocalEmulator(backend_type=self.MockEmulatorBackend, runs=123)

        config_repr = json.loads(backend._emulation_config.to_abstract_repr())
        bitstrings_repr = config_repr["observables"][0]
        assert bitstrings_repr["num_shots"] == 123

    def test_emulator_backend_default_config(self) -> None:
        backend = LocalEmulator(backend_type=self.MockEmulatorBackend)

        expected_config = backend.default_emulation_config()
        # convert the expected config to a str
        expected_config_repr = json.loads(expected_config.to_abstract_repr())
        expected_obs_repr = expected_config_repr.pop("observables")

        config = backend._emulation_config
        assert isinstance(config, EmulationConfig)
        # convert the saved config to a str
        config_repr = json.loads(config.to_abstract_repr())
        obs_repr = config_repr.pop("observables")

        assert expected_config_repr == config_repr
        # uuid is expected to be different for each instance
        for obs, expected_obs in zip(obs_repr, expected_obs_repr):
            expected_obs.pop("uuid")
            obs.pop("uuid")
            assert obs == expected_obs

    def test_check_backend_type(self) -> None:
        with pytest.raises(match="`backend_type` must be a EmulatorBackend type."):
            LocalEmulator(backend_type=int)  # type: ignore

        with pytest.raises(match="`backend_type` must be a RemoteEmulatorBackend type."):
            RemoteEmulator(backend_type=str, connection=self.mock_connection)  # type: ignore

    def test_validate_connection(self) -> None:
        backend = RemoteEmulator(
            backend_type=self.MockRemoteEmulatorBackend, connection=self.mock_connection
        )
        connection = backend.validate_connection(self.mock_connection)
        assert connection is self.mock_connection

        with pytest.raises(match=f"""Error in `PulserRemoteBackend`:
                `connection` must be of type {RemoteConnection}."""):
            backend.validate_connection(4.0)  # type: ignore

    def test_local_emulator_run(self) -> None:
        backend = LocalEmulator(backend_type=self.MockEmulatorBackend)
        backend.run(self.mock_program_compiled)
        assert isinstance(backend._backend, self.MockEmulatorBackend)
        # assert called once
        assert backend._backend.run_calls == 1

    def test_remote_run(self) -> None:
        backend = RemoteEmulator(
            backend_type=self.MockRemoteEmulatorBackend, connection=self.mock_connection
        )
        backend.run(self.mock_program_compiled)
        assert isinstance(backend._backend, self.MockRemoteEmulatorBackend)
        # assert called once
        assert backend._backend.run_calls == 1

    def test_qpu_init(self) -> None:
        qpu = QPU(connection=self.mock_connection, runs=123)
        assert qpu._backend_type == QPUBackend
        assert qpu._connection is self.mock_connection
        config = qpu._config
        assert isinstance(config, BackendConfig)
        assert config.default_num_shots == 123

    def test_qpu_init_no_runs(self) -> None:
        with pytest.raises(
            ValueError, match="Number of runs must be provided to use the QPU backend."
        ):
            QPU(connection=self.mock_connection)
