from __future__ import annotations

import datetime
import json
import random
from collections import Counter
from typing import Any, Callable

import pulser
import pytest
from emu_mps import MPSBackend
from emu_sv import SVBackend
from pasqal_cloud.utils.mock_server import BaseMockServer
from pulser.backend.abc import EmulatorBackend
from pulser.sequence import Sequence as PulserSequence
from pulser_pasqal import PasqalCloud
from pulser_pasqal.backends import EmuFreeBackendV2, EmuMPSBackend, RemoteEmulatorBackend
from pulser_simulation import QutipBackendV2

from qoolqit.devices import ALL_DEVICES
from qoolqit.execution import CompilerProfile, LocalEmulator, RemoteEmulator
from qoolqit.program import QuantumProgram


@pytest.mark.flaky(max_runs=2)
@pytest.mark.parametrize("device_class", ALL_DEVICES)
@pytest.mark.parametrize("profile", CompilerProfile.list())
@pytest.mark.parametrize(
    "backend_type",
    [
        QutipBackendV2,
        SVBackend,
        MPSBackend,
    ],
)
@pytest.mark.parametrize("runs", [500, 100])
def test_local_backend_run(
    device_class: Callable,
    profile: CompilerProfile,
    random_program: Callable[[], QuantumProgram],
    backend_type: type[EmulatorBackend],
    runs: int,
) -> None:

    # FIXME: Reactivate the min_distance profile once we implement safe-mode compilation
    # Currently trying to set the atoms at the min distance will very often cause the
    # amplitude to go over the limit allowed for the channel, which will fail the compilation.
    if profile != CompilerProfile.MIN_DISTANCE:
        program = random_program()
        device = device_class()
        program.compile_to(device, profile=profile)

        local_emulator = LocalEmulator(backend_type=backend_type, runs=runs)
        results = local_emulator.run(program)
        assert results
        bitstrings = results[-1].final_bitstrings
        assert sum(bitstrings.values()) == runs


# @pytest.mark.skip(reason="Remote not working")
@pytest.mark.parametrize("device_class", ALL_DEVICES)
@pytest.mark.parametrize("profile", CompilerProfile.list())
@pytest.mark.parametrize("backend_type", [EmuMPSBackend, EmuFreeBackendV2])
@pytest.mark.parametrize("runs", [500, 100])
def test_compiler_profiles_dmm(
    device_class: Callable,
    profile: CompilerProfile,
    dmm_program: Callable[[], QuantumProgram],
    backend_type: type[RemoteEmulatorBackend],
    runs: int,
) -> None:
    class MyMockServer(BaseMockServer):

        # Override any endpoints.
        def __init__(self) -> None:
            super().__init__()
            self.mocker.get("http://example.com/results/my-results", json=self.my_results)
            self._iterations = 0
            self._start = str(datetime.datetime.now())
            self._runs = None
            self._sequence_builder = ""
            self._register = ""

        def endpoint_get_devices_specs(self, request: Any, context: Any, matches: list[str]) -> Any:
            """Return a basic device called `DigitalAnalogDevice`."""
            return {
                "data": {"DigitalAnalogDevice": pulser.DigitalAnalogDevice.to_abstract_repr()},
            }

        def endpoint_get_devices_public_specs(
            self, request: Any, context: Any, matches: list[str]
        ) -> Any:
            """Return a basic device called `DigitalAnalogDevice`."""
            return {
                "data": [
                    {
                        "device_type": "DigitalAnalogDevice",
                        "specs": pulser.DigitalAnalogDevice.to_abstract_repr(),
                    },
                ],
            }

        def endpoint_post_batch(self, request: Any, context: Any, matches: list[str]) -> Any:
            batch: dict[str, Any] = json.loads(request.text)
            data = self.add_batch(batch)
            return {
                "data": data,
            }

        def endpoint_get_batch(self, request: Any, context: Any, matches: list[str]) -> Any:
            """Mock for GET /api/v1/batches/{batch_id}."""
            assert matches[0] == "my-mock-batch-id"

            if self._iterations < 5:
                self._iterations += 1
                # Initially, respond that the batch is pending.
                return {
                    "data": {
                        "open": False,
                        "complete": False,
                        "created_at": self._start,
                        "updated_at": str(datetime.datetime.now()),
                        "project_id": "my-project-id",
                        "id": "my-mock-batch-id",
                        "user_id": "my-user-id",
                        "status": "PENDING",
                        "ordered_jobs": [],
                        "device_type": "DigitalAnalogDevice",
                        "sequence_builder": self._sequence_builder,
                    }
                }

            return {
                "data": {
                    "open": False,
                    "complete": False,
                    "created_at": self._start,
                    "updated_at": str(datetime.datetime.now()),
                    "project_id": "my-project-id",
                    "id": "my-mock-batch-id",
                    "user_id": "my-user-id",
                    "status": "DONE",
                    "ordered_jobs": [],
                    "device_type": "DigitalAnalogDevice",
                    "sequence_builder": self._sequence_builder,
                }
            }

        def endpoint_get_jobs(self, request: Any, context: Any, matches: list[str]) -> Any:
            return {
                "code": 200,
                "data": [
                    {
                        "id": "my-job-id",
                        "parent-id": "my-parent-id",
                        "status": "DONE",
                        "runs": self._runs,
                        "batch_id": "my-match-id",
                        "project_id": "my-project-id",
                        "created_at": self._start,
                        "updated_at": str(datetime.datetime.now()),
                        "creation_order": 0,
                        "sequence_builder": self._sequence_builder,
                    }
                ],
                "message": "OK.",
                "status": "success",
            }

        def add_batch(self, batch: Any) -> Any:
            assert batch["project_id"] == "my-project-id"
            self._runs = batch["jobs"][0]["runs"]
            self._sequence_builder = batch["sequence_builder"]
            self._register = json.loads(self._sequence_builder)["register"]
            return {
                "open": False,
                "complete": False,
                "created_at": self._start,
                "updated_at": str(datetime.datetime.now()),
                "project_id": batch["project_id"],
                "id": "my-mock-batch-id",
                "user_id": "my-user-id",
                "status": "PENDING",
                "ordered_jobs": [],
                "device_type": "DigitalAnalogDevice",
                "sequence_builder": self._sequence_builder,
            }

        def my_results(self, request: Any, context: Any) -> Any:
            counter: Counter[str] = Counter()
            assert isinstance(self._runs, int)
            for _ in range(self._runs):
                # Generate key
                bitstr: str = ""
                for _ in range(len(self._register)):
                    bitstr += str(random.randrange(0, 2))
                counter[bitstr] += 1
            return {"counter": counter}

        def endpoint_get_job_results(self, request: Any, context: Any, matches: list[str]) -> Any:
            return {
                "data": {
                    "results_link": "http://example.com/results/my-results",
                },
            }

    if profile != CompilerProfile.MIN_DISTANCE:
        with MyMockServer():
            USERNAME = "my_username"
            PROJECT_ID = "my-project-id"
            PASSWORD = "my_password"
            connexion = PasqalCloud(
                username=USERNAME,
                password=PASSWORD,
                project_id=PROJECT_ID,
            )
            remote_emulator = RemoteEmulator(
                backend_type=backend_type, connection=connexion, runs=runs
            )
            program = dmm_program()
            device = device_class()
            if device._device.dmm_channels:
                program.compile_to(device, profile=profile)
                assert program.is_compiled
                assert isinstance(program.compiled_sequence, PulserSequence)

                results = remote_emulator.run(program)
                assert results
