from __future__ import annotations

from collections.abc import Sequence
from unittest.mock import MagicMock

import pytest

from pulser.backend import EmulatorBackend, Results, EmulationConfig, BitStrings
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import RemoteConnection, RemoteResults
from pulser.sequence import Sequence as PulserSequence
from pulser_pasqal.backends import RemoteEmulatorBackend as PasqalRemoteEmulatorBackend

from qoolqit.execution import LocalEmulator, RemoteEmulator, QPU
from qoolqit.program import QuantumProgram


@pytest.fixture(autouse=True)
def reset_counters():
    """Reset invocation counters on all mock backends before each test.

    All mock backends track two pieces of state:
      - run_calls: number of times run() was invoked.
      - last_instance: last created backend instance.

    The autouse fixture guarantees that each test starts with a clean state,
    preventing cross-test contamination and ensuring deterministic assertions.
    """
    TestMimicQPU.MockLocalBackend.run_calls = 0
    TestMimicQPU.MockRemoteEmulatorBackend.run_calls = 0
    TestMimicQPU.MockQPUBackend.run_calls = 0


class TestMimicQPU:
    """TestMimiqQPU class.
    """

    # Common test objects
    mock_seq = MagicMock(spec=PulserSequence)
    mock_program = MagicMock(spec=QuantumProgram, compiled_sequence=mock_seq)
    mock_connection = MagicMock(spec=RemoteConnection)

    class MockLocalBackend(EmulatorBackend):
        """MockLocalBackend class.
        A mock implementation of a local emulator backend used for unit tests.

        This backend:
          - records constructor calls,
          - stores the last created instance,
          - increments run_calls on each run() invocation,
          - exposes _mimic_qpu to validate propagation through LocalEmulator.
        """
        run_calls = 0
        last_instance = None
        default_config = EmulationConfig(observables=(BitStrings(num_shots=1),))

        @staticmethod
        def validate_sequence(sequence, mimic_qpu=False):
            pass

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            TestMimicQPU.MockLocalBackend.last_instance = self

        def run(self):
            type(self).run_calls += 1
            return MagicMock(spec=Results)

    # Remote emulator mock 
    class MockRemoteEmulatorBackend(PasqalRemoteEmulatorBackend):
        """MockRemoteEmulatorBackend class.
        A mock implementation of a backend for remote emulator scenarios.

        This backend mirrors the real RemoteEmulatorBackend behaviour:
          - accepts connection and mimic_qpu explicitly,
          - increments run counter,
          - tracks last instantiated object for validation.
        """
        run_calls = 0
        last_instance = None
        default_config = EmulationConfig(observables=(BitStrings(num_shots=1),))

        @staticmethod
        def validate_sequence(sequence, mimic_qpu=False):
            pass

        def __init__(self, sequence, *, connection, config=None, mimic_qpu=False):
            super().__init__(sequence, connection=connection, mimic_qpu=mimic_qpu, config=config)
            TestMimicQPU.MockRemoteEmulatorBackend.last_instance = self

        def run(self, job_params=None, wait=False):
            type(self).run_calls += 1
            return MagicMock(spec=RemoteResults)

    # QPU mock backend 
    class MockQPUBackend(QPUBackend):
        """MockQPUBackend class
        A mock implementation of a QPU backend.

        Used to verify that QPU wrapper classes pass mimic_qpu correctly to QPU backend constructor.
        """
        last_instance = None
        run_calls = 0

        @staticmethod
        def validate_sequence(sequence, mimic_qpu=False):
            pass

        def __init__(self, sequence, *, connection, mimic_qpu=False):
            super().__init__(sequence, connection=connection)
            self._mimic_qpu = mimic_qpu
            TestMimicQPU.MockQPUBackend.last_instance = self

        def run(self, job_params=None, wait=False):
            type(self).run_calls += 1
            return MagicMock(spec=RemoteResults)

    # LocalEmulator tests 
    def test_local_mimic_qpu_true(self):
        """Verify that LocalEmulator forwards mimic_qpu=True to the backend.

        Ensures:
          - the instantiated backend receives _mimic_qpu = True,
          - run() is invoked once on the backend.
        """
        backend = LocalEmulator(
            backend_type=self.MockLocalBackend,
            mimic_qpu=True,
        )
        backend.run(self.mock_program)
        inst = self.MockLocalBackend.last_instance
        assert inst._mimic_qpu is True
        assert inst.run_calls == 1


    def test_local_mimic_qpu_default_is_false(self):
        """Verify the default value mimic_qpu=False is used when omitted.

        Ensures default behaviour aligns with Pulser backend expectations.
        """
        backend = LocalEmulator(
            backend_type=self.MockLocalBackend
        )
        backend.run(self.mock_program)
        inst = self.MockLocalBackend.last_instance
        assert inst._mimic_qpu is False
        assert inst.run_calls == 1

    # RemoteEmulator tests 
    def test_remote_emulator_mimic_qpu_true(self):
        """Verify RemoteEmulator correctly propagates mimic_qpu=True."""
        backend = RemoteEmulator(
            backend_type=self.MockRemoteEmulatorBackend,
            connection=self.mock_connection,
            mimic_qpu=True,
        )
        backend.run(self.mock_program)
        inst = self.MockRemoteEmulatorBackend.last_instance
        assert inst._mimic_qpu is True
        assert inst.run_calls == 1


    def test_remote_emulator_mimic_qpu_default_is_false(self):
        """Ensure mimic_qpu defaults to False when not specified."""
        backend = RemoteEmulator(
            backend_type=self.MockRemoteEmulatorBackend,
            connection=self.mock_connection,
        )
        backend.run(self.mock_program)
        inst = self.MockRemoteEmulatorBackend.last_instance
        assert inst._mimic_qpu is False
        assert inst.run_calls == 1



