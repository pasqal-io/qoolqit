from __future__ import annotations

import logging
import time
from abc import abstractmethod
from typing import Counter, cast

import pulser
import pulser.backend.remote
from pasqal_cloud import SDK, EmulatorType
from pasqal_cloud.batch import Batch
from pulser import Sequence
from pulser.backend.remote import BatchStatus, RemoteResults
from pulser.devices import Device
from pulser.json.abstract_repr.deserializer import deserialize_device
from pulser.result import SampledResult
from pulser_myqlm import PulserQLMConnection

from qoolqit._solvers.data import (
    BackendConfig,
    BaseJob,
    CompilationError,
    JobId,
    NamedDevice,
    QuantumProgram,
    Result,
)
from qoolqit._solvers.types import DeviceType

from .base_backend import BaseBackend, make_sequence

logger = logging.getLogger(__name__)


############################ Remote backends


class RemoteJob(BaseJob):
    def __init__(self, sdk: SDK, id: JobId, sleep_duration_sec: float = 10):
        super().__init__(id=id)
        self._sdk = sdk
        self._batch: Batch | None = None
        self._result: Result | None = None
        self._error: Exception | None = None
        self._status: BatchStatus = BatchStatus.PENDING
        self.sleep_duration_sec = sleep_duration_sec

    @classmethod
    def _convert_status(cls, status: str) -> BatchStatus:
        if status == "PENDING":
            return BatchStatus.PENDING
        if status == "RUNNING":
            return BatchStatus.RUNNING
        if status == "DONE":
            return BatchStatus.DONE
        if status == "CANCELED":
            return BatchStatus.CANCELED
        if status == "TIMED_OUT":
            return BatchStatus.TIMED_OUT
        if status == "ERROR":
            return BatchStatus.ERROR
        if status == "PAUSED":
            return BatchStatus.PAUSED
        raise ValueError(f"Invalid status '{status}'")

    def status(self) -> BatchStatus:
        if (
            self._status == BatchStatus.PENDING
            or self._status == BatchStatus.RUNNING
            or self._status == BatchStatus.PAUSED
        ):
            # Fetch latest status.
            batch = self._sdk.get_batch(id=self.id)
            self._status = self._convert_status(batch.status)
        return self._status

    def wait(self) -> Result:
        if self._result is not None:
            return self._result
        if self._error is not None:
            raise self._error

        batch = self._sdk.get_batch(id=self.id)

        # Wait for execution to complete.
        while True:
            time.sleep(self.sleep_duration_sec)
            batch.refresh()
            if batch.status in {"PENDING", "RUNNING"}:
                # Continue waiting.

                continue
            job = batch.ordered_jobs[0]
            if job.status == "ERROR":
                self._error = Exception(f"Error while executing remote job: {job.errors}")
                # FIXME: This is subject to race condition.
                raise self._error
            counter = job.result
            assert isinstance(counter, dict)
            counter = cast(Counter[str], counter)

            # FIXME: This is subject to race condition.
            self._result = Result(counts=counter)

            return self._result


class BaseRemoteBackend(BaseBackend):
    """
    Base hierarch for remote backends.

    Performance warning:
        As of this writing, using remote Backends to access a remote QPU or remote emulator
        is slower than using a RemoteExtractor, as the RemoteExtractor optimizes the number
        of connections used to communicate with the cloud server.
    """

    def __init__(self, config: BackendConfig):
        super().__init__(config)
        self._sdk = SDK(
            username=self.config.username,
            project_id=self.config.project_id,
            password=self.config.password,
        )
        self._max_runs: int | None = None
        self._device: Device | None = None

    def _api_max_runs(self) -> int:
        # As of this writing, the API doesn't support runs longer than 500 jobs.
        # If we want to add more runs, we'll need to split them across several jobs.
        return 500

    def device(self) -> Device:
        """Make sure that we have fetched the latest specs for the device from the server."""
        if self._device is not None:
            assert self._max_runs is not None
            return self._device

        # Fetch the latest list of QPUs
        device_key = None
        if isinstance(self.config.device, NamedDevice):
            device_key = self.config.device
        elif self.config.device is None:
            device_key = NamedDevice("FRESNEL")
        if device_key is not None:
            specs = self._sdk.get_device_specs_dict()
            if device_key not in specs:
                raise ValueError(
                    f"Unknown device {self.config.device}, "
                    + f"available devices are {list(specs.keys())}"
                )
            self._device = cast(Device, deserialize_device(specs[device_key]))
        else:
            assert isinstance(self.config.device, DeviceType)
            self._device = self.config.device.value
        self._max_runs = self._device.max_runs
        return self._device

    @abstractmethod
    def _execute_remotely(self, sequence: Sequence, runs: int) -> JobId:
        """Enqueue execution of a Pulser sequence."""
        ...

    def submit(self, program: QuantumProgram, runs: int | None = None) -> BaseJob:
        """
        Run the pulse + register.

        Raises:
            CompilationError: If the register/pulse may not be executed on this device.
        """
        try:
            sequence = make_sequence(program)
        except ValueError as e:
            raise CompilationError(f"This register/pulse cannot be executed on the device: {e}")
        if runs is None:
            runs = 500
        runs = min(runs, self._api_max_runs())
        id = self._execute_remotely(sequence, runs)
        return RemoteJob(sdk=self._sdk, id=id)

    def proceed(self, job: JobId) -> BaseJob:
        return RemoteJob(sdk=self._sdk, id=job)


class RemoteQPUBackend(BaseRemoteBackend):
    """
    Execute on a remote QPU.

    Performance note:
        As of this writing, the waiting lines for a QPU
        may be very long. You may use this Extractor to resume your workflow
        with a computation that has been previously started.
    """

    def __init__(self, config: BackendConfig):
        super().__init__(config)

    def _execute_remotely(self, sequence: Sequence, runs: int) -> JobId:
        batch = self._sdk.create_batch(
            serialized_sequence=sequence.to_abstract_repr(),
            jobs=[{"runs": runs}],
            wait=False,
            emulator=None,
            configuration=None,
        )
        return JobId(batch.id)


class RemoteEmuMPSBackend(BaseRemoteBackend):
    """
    A backend that uses a remote high-performance emulator (EmuMPS).

    published on Pasqal Cloud.
    """

    def _execute_remotely(self, sequence: Sequence, runs: int) -> JobId:
        batch = self._sdk.create_batch(
            serialized_sequence=sequence.to_abstract_repr(),
            jobs=[{"runs": runs}],
            wait=False,
            emulator=EmulatorType.EMU_MPS,
            configuration=None,
        )
        return JobId(batch.id)


class RemoteEmuTNBackend(BaseRemoteBackend):
    """
    A backend that uses a remote high-performance emulator (EmuSV).

    published on Pasqal Cloud.
    """

    def _execute_remotely(self, sequence: Sequence, runs: int) -> JobId:
        batch = self._sdk.create_batch(
            serialized_sequence=sequence.to_abstract_repr(),
            jobs=[{"runs": runs}],
            wait=False,
            emulator=EmulatorType.EMU_TN,
            configuration=None,
        )
        return JobId(batch.id)


class RemoteEmuFREEBackend(BaseRemoteBackend):
    """
    A backend that uses a remote high-performance emulator (EmuFREE).

    published on Pasqal Cloud.
    """

    def _execute_remotely(self, sequence: Sequence, runs: int) -> JobId:
        batch = self._sdk.create_batch(
            serialized_sequence=sequence.to_abstract_repr(),
            jobs=[{"runs": runs}],
            wait=False,
            emulator=EmulatorType.EMU_FREE,
            configuration=None,
        )
        return JobId(batch.id)


# --- QLM specific


class RemoteQLMQPUBackend(BaseBackend):
    def __init__(self, config: BackendConfig):
        super().__init__(config)

        self._device = None
        self._max_runs = None

        # The documentation of the constructor mentions that it's possible
        # to pass a username/password, but digging into the code doesn't
        # seem to confirm it, so we assume that users of MyQLM use another
        # auth mechanism.
        if config.username is not None or config.password is not None:
            logger.warning(
                "ignoring username/password for the QLM backend "
                + "in favor of external authentication"
            )
        self._connection = PulserQLMConnection()

    def _api_max_runs(self) -> int:
        # Arbitrary number, matching RemoteQPUBackend.
        return 500

    def _default_max_runs(self) -> int:
        # Arbitrary number, matching RemoteQPUBackend.
        return 500

    def device(self) -> Device:
        """Make sure that we have fetched the latest specs for the device from the server."""
        if self._device is not None:
            assert self._max_runs is not None
            return self._device

        # Fetch the latest list of QPUs
        device_key = None
        if isinstance(self.config.device, NamedDevice):
            device_key = self.config.device
        elif self.config.device is None:
            device_key = NamedDevice("FRESNEL")
        if device_key is not None:
            specs = self._connection.fetch_available_devices()
            if device_key not in specs:
                raise ValueError(
                    f"Unknown device {self.config.device}, "
                    + f"available devices are {list(specs.keys())}"
                )
            device = specs[device_key]
        else:
            assert isinstance(self.config.device, DeviceType)
            device = self.config.device.value
        self._device = device
        self._max_runs = (
            device.max_runs if device.max_runs is not None else self._default_max_runs()
        )
        return device

    def submit(self, program: QuantumProgram, runs: int | None = None) -> BaseJob:
        """
        Run the pulse + register.

        Raises:
            CompilationError: If the register/pulse may not be executed on this device.
        """
        try:
            sequence = make_sequence(program)
        except ValueError as e:
            raise CompilationError(f"This register/pulse cannot be executed on the device: {e}")
        if runs is None:
            runs = 500
        runs = min(runs, self._api_max_runs())
        results = self._execute_remotely(sequence, runs)
        return RemoteQLMJob(results=results)

    def proceed(self, job: JobId) -> BaseJob:
        # We may need to change the signature of this method, as we can't simply fetch
        # a job from just its job id, we also need its batch id.
        raise NotImplementedError

    def _execute_remotely(self, sequence: Sequence, runs: int) -> RemoteResults:
        return self._connection.submit(sequence, wait=False, open=False, runs=runs)


class RemoteQLMJob(BaseJob):
    """
    An adapter from pulser.backend.remote.RemoteResults to BaseJob.

    In the future, we expect to progressively migrate all of BaseJob
    to use RemoteResults.
    """

    def __init__(
        self, results: pulser.backend.remote.RemoteResults, sleep_duration_sec: float = 10
    ):
        assert len(results.job_ids) == 1
        super().__init__(JobId(results.job_ids[0]))
        self._remote_results = results
        self._result: Result | None = None
        self.sleep_duration_sec = sleep_duration_sec

    def status(self) -> BatchStatus:
        # As of this writing, we don't have a way to fetch the status.
        if self._result is not None:
            return BatchStatus.DONE
        return BatchStatus.PENDING

    def wait(self) -> Result:
        if self._result is not None:
            return self._result

        # Wait for execution to complete.
        while True:
            time.sleep(self.sleep_duration_sec)
            results = self._remote_results.get_available_results()
            if len(results) != 1:
                logger.info("We're still expecting the results to job %s", self.id)
                self._status = BatchStatus.PENDING
                continue

            # From this point, we assume that len(expected) == 1, as this is the only
            # way to construct a `RemoteQMLJob`.
            result = results[self.id]
            assert isinstance(result, SampledResult)

            # FIXME: This is subject to race condition.
            self._result = Result(counts=Counter(result.bitstring_counts))

            return self._result
