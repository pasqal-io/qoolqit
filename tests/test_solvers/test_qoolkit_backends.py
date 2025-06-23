from __future__ import annotations

import abc
import datetime
import json
import os
import random
import re
from typing import Any, Callable, Counter
from uuid import uuid4

import pulser
import pulser.pulse
import pytest
import requests_mock
from pasqal_cloud.endpoints import Endpoints

from qoolqit.solvers import backends
from qoolqit.solvers.backends import (
    BackendConfig,
    BackendType,
    BaseBackend,
    NamedDevice,
    QuantumProgram,
    RemoteJob,
    get_backend,
)


def make_simple_program(backend: BaseBackend) -> QuantumProgram:
    return QuantumProgram(
        device=backend.device(),  # Use the default device
        register=pulser.Register({"q0": [0.0, 0.0], "q1": [10.0, 10.0]}),
        pulse=pulser.pulse.Pulse.ConstantPulse(
            duration=100,
            amplitude=0.5,
            phase=0.5,
            detuning=0,
        ),
    )


local_backends: list[tuple[type[BaseBackend], BackendType]] = [
    (backends.QutipBackend, BackendType.QUTIP),
]
if os.name == "posix":
    local_backends += [
        (backends.EmuMPSBackend, BackendType.EMU_MPS),
        (backends.EmuSVBackend, BackendType.EMU_SV),
    ]

remote_backends: list[tuple[type[BaseBackend], BackendType]] = [
    (backends.RemoteEmuMPSBackend, BackendType.REMOTE_EMUMPS),
    (backends.RemoteQPUBackend, BackendType.REMOTE_QPU),
]

all_backends = local_backends + remote_backends


def test_get_backend() -> None:
    """Test that `get_backend()` successfully instantiates backends of the right type."""
    for cls, type in all_backends:
        backend_config = BackendConfig(backend=type)
        backend = get_backend(backend_config)
        assert isinstance(backend, cls)


@pytest.mark.parametrize("backend_kind", local_backends)
@pytest.mark.parametrize("num_shots", [1, 10, 100])
def test_local_execute(backend_kind: tuple[type[BaseBackend], BackendType], num_shots: int) -> None:
    """Test that we can run locally a simple quantum program works."""
    backend_config = BackendConfig(
        backend=backend_kind[1],
    )
    backend = get_backend(backend_config)
    program = make_simple_program(backend)
    result = backend.run(program, num_shots)
    assert len(result.counts) >= 1
    assert len(result) == num_shots
    for k in result.counts.keys():
        assert len(k) == 2  # Two qubits


# This class is in the process of moving to pasqal-cloud, see https://github.com/pasqal-io/pasqal-cloud/pull/190.
class BaseMockServer(abc.ABC):
    """
    A mock server used as a replacement for the Pasqal HTTP server during testing.

    Intended use:
    ```
    class MyMockServer(BaseMockServer):
        raise NotImplementedError

    with MyMockServer():
        client = Client()
        # raise NotImplementedError perform usual operations on the client
    ```
    """

    def __init__(self, endpoints: Endpoints | None = None):
        self.mocker = requests_mock.Mocker()
        self.endpoints = endpoints
        if self.endpoints is None:
            self.endpoints = Endpoints()

        re_path_variables = re.compile("{([a-z_]+)}")

        # Install mocks for each endpoint.
        for method, relative_url, impl in [
            ("POST", "/api/v1/batches", self.endpoint_post_batch),
            ("GET", "/api/v2/batches/{batch_id}", self.endpoint_get_batch),
            (
                "GET",
                "/api/v1/jobs/{job_id}/results_link",
                self.endpoint_get_job_results,
            ),
            (
                "PATCH",
                "/api/v2/batches/{batch_id}/complete",
                self.endpoint_patch_close_batch,
            ),
            (
                "PATCH",
                "/api/v2/batches/{batch_id}/cancel",
                self.endpoint_patch_cancel_batch,
            ),
            ("PATCH", "/api/v2/batches/cancel", self.endpoint_patch_cancel_batches),
            ("POST", "/api/v1/batches/{batch_id}/rebatch", self.endpoint_post_rebatch),
            ("GET", "/api/v2/jobs", self.endpoint_get_jobs),
            ("PATCH", "/api/v2/jobs/{job_id}/cancel", self.endpoint_cancel_job),
            (
                "PATCH",
                "/api/v2/batches/{batch_id}/cancel/jobs",
                self.endpoint_cancel_jobs,
            ),
            ("POST", "/api/v1/workloads", self.endpoint_post_workload),
            ("GET", "/api/v2/workloads/{workload_id}", self.endpoint_get_workload),
            (
                "PUT",
                "/api/v1/workloads/{workload_id}/cancel",
                self.endpoint_put_cancel_workload,
            ),
            ("GET", "/api/v1/devices/specs", self.endpoint_get_devices_specs),
            (
                "GET",
                "/api/v1/devices/public-specs",
                self.endpoint_get_devices_public_specs,
            ),
        ]:
            rewritten_relative_url = re.sub(
                pattern=re_path_variables,
                repl=lambda m: f"(?P<{m.group(1)}>[^\\\\]*)",
                string=relative_url,
            )
            escaped_full_url = re.escape(self.endpoints.core) + rewritten_relative_url
            compiled_full_url = re.compile(escaped_full_url)

            def wrapper(
                request: Any,
                context: Any,
                # Capture from current loop iteration.
                impl: Callable[[Any, Any, list[str]], Any] = impl,
                compiled_full_url: re.Pattern[str] = compiled_full_url,
            ) -> Any:
                matches: list[str] = compiled_full_url.findall(request.url)
                return impl(request, context, matches)

            self.mocker.request(method=method, url=compiled_full_url, json=wrapper)
        self.mocker.request(
            method="POST",
            url="https://authenticate.pasqal.cloud/oauth/token",
            json=self.endpoint_post_authenticate_token,
        )

    def __enter__(self) -> None:
        self.mocker.__enter__()

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        self.mocker.__exit__(type, value, traceback)

    def endpoint_post_authenticate_token(self, request: Any, context: Any) -> Any:
        """Mock for POST https://authenticate.pasqal.cloud/oauth/token."""
        token = "mock-token-" + str(uuid4())
        return {
            "expires-in": 100000000,
            "access_token": token,
        }

    def endpoint_post_batch(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for POST /api/v1/batches."""
        raise NotImplementedError

    def endpoint_get_batch(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for GET /api/v1/batches/{batch_id}."""
        raise NotImplementedError

    def endpoint_get_job_results(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for GET /api/v1/jobs/{job_id}/results_link."""
        raise NotImplementedError

    def endpoint_patch_close_batch(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for PATCH /api/v2/batches/{batch_id}/complete."""
        raise NotImplementedError

    def endpoint_patch_cancel_batch(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for PATCH /api/v2/batches/{batch_id}/cancel."""
        raise NotImplementedError

    def endpoint_patch_cancel_batches(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for PATCH /api/v2/batches/cancel."""
        raise NotImplementedError

    def endpoint_post_rebatch(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for POST /api/v2/batches/{batch_id}/rebatch."""
        raise NotImplementedError

    def endpoint_get_jobs(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for GET /api/v2/jobs."""
        raise NotImplementedError

    def endpoint_get_batches(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for GET /api/v1/batches."""
        raise NotImplementedError

    def endpoint_add_jobs(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for POST /api/v2/batches/{batch_id}/jobs."""
        raise NotImplementedError

    def endpoint_cancel_job(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for PATCH /api/v2/jobs/{job_id}/cancel."""
        raise NotImplementedError

    def endpoint_cancel_jobs(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for PATCH /api/v2/batches/{batch_id}/cancel/jobs."""
        raise NotImplementedError

    def endpoint_post_workload(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for POST /api/v1/workloads."""
        raise NotImplementedError

    def endpoint_get_workload(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for GET /api/v1/workloads/{workload_id}."""
        raise NotImplementedError

    def endpoint_put_cancel_workload(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for PUT /api/v1/workloads/{workload_id}/cancel."""
        raise NotImplementedError

    def endpoint_get_devices_specs(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for GET /api/v1/devices/specs."""
        raise NotImplementedError

    def endpoint_get_devices_public_specs(
        self, request: Any, context: Any, matches: list[str]
    ) -> Any:
        """Mock for GET /api/v1/devices/public-specs."""
        raise NotImplementedError

    def endpoint_patch_batch_tags(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Mock for PATCH /api/v1/batches/{batch_id}/tags."""
        raise NotImplementedError


class MyMockServer(BaseMockServer):
    def __init__(self) -> None:
        super().__init__()
        self.mocker.get("http://example.com/results/my-results", json=self.my_results)
        self._iterations = 0
        self._start = str(datetime.datetime.now())
        self._runs = None

    def endpoint_get_devices_specs(self, request: Any, context: Any, matches: list[str]) -> Any:
        """Return a basic device called `MY_DEVICE`."""
        return {
            "data": {"MY_DEVICE": pulser.AnalogDevice.to_abstract_repr()},
        }

    def endpoint_get_devices_public_specs(
        self, request: Any, context: Any, matches: list[str]
    ) -> Any:
        """Return a basic device called `MY_DEVICE`."""
        return {
            "data": [
                {
                    "device_type": "MY_DEVICE",
                    "specs": pulser.AnalogDevice.to_abstract_repr(),
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
                    "device_type": "AnalogDevice",
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
                "device_type": "AnalogDevice",
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
                }
            ],
            "message": "OK.",
            "status": "success",
        }

    def add_batch(self, batch: Any) -> Any:
        assert batch["project_id"] == "my-project-id"
        self._runs = batch["jobs"][0]["runs"]
        self._register = json.loads(batch["sequence_builder"])["register"]
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
            "device_type": "AnalogDevice",
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


@pytest.mark.parametrize("backend_kind", remote_backends)
@pytest.mark.parametrize("num_shots", [1, 10, 100])
def test_remote_execute(
    backend_kind: tuple[type[BaseBackend], BackendType], num_shots: int
) -> None:
    """Test that we can run remotely a simple quantum program works."""
    backend_config = BackendConfig(
        backend=backend_kind[1],
        username="my_username",
        password="my_password",
        project_id="my-project-id",
        device=NamedDevice("MY_DEVICE"),
    )
    with MyMockServer():
        backend = get_backend(backend_config)
        device = backend.device()
        assert device.name == "AnalogDevice"
        program = make_simple_program(backend)
        job = backend.submit(program, num_shots)
        assert job.id == "my-mock-batch-id"
        assert isinstance(job, RemoteJob)
        job.sleep_duration_sec = 0.1  # Speed up test
        result = job.wait()
        assert len(result.counts) >= 1
        assert len(result) == num_shots
        for k in result.counts.keys():
            assert len(k) == 2  # Two qubits
