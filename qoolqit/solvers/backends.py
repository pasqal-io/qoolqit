from __future__ import annotations

import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Counter, cast
from uuid import uuid4

import pulser
import pydantic
from pasqal_cloud import SDK, EmulatorType
from pasqal_cloud.batch import Batch
from pulser import Sequence
from pulser.backend.remote import BatchStatus
from pulser.devices import Device
from pulser.json.abstract_repr.deserializer import deserialize_device
from pulser_simulation import QutipEmulator

from .types import BackendType, DeviceType

logger = logging.getLogger(__name__)


@dataclass
class QuantumProgram:
    """
    Placeholder for qoolqit.QuantumProgram
    """

    device: pulser.devices.Device
    register: pulser.Register
    pulse: pulser.Pulse


pydantic.BaseModel.model_config["arbitrary_types_allowed"] = True


class NamedDevice(str):
    """
    An individual, named, device, e.g. "FRESNEL".
    """

    pass


class BackendConfig(pydantic.BaseModel):
    """
    Generic configuration for backends.
    """

    backend: BackendType = BackendType.QUTIP
    """
    The type of backend to use.

    If None, pick a reasonable default backend running locally.
    """

    username: str | None = None
    """
    For a backend that requires authentication, such as Pasqal Cloud,
    the username.

    Otherwise, ignored.
    """

    password: str | None = None
    """
    For a backend that requires authentication, such as Pasqal Cloud,
    the password.

    Otherwise, ignored.
    """

    project_id: str | None = None
    """
    For a backend that associates jobs to projects, such as Pasqal Cloud,
    the id of the project. The project must already exist.

    Otherwise, ignored.
    """

    device: NamedDevice | DeviceType | None = None
    """
    For a backend that supports numerous devices, either:

    - a type of device (e.g. `DeviceType.ANALOG_DEVICE`); or
    - the name of a specific device (e.g. `NamedDevice("FRESNEL")`).

    If unspecified, pick a backend-appropriate device.
    """

    dt: int = 10
    """
    For a backend that supports customizing the duration of steps, the
    timestep size.

    As of this writing, this parameter is used only by the EmuMPS backends.
    """


class CompilationError(Exception):
    """
    An error raised when attempting to compile a graph for an architecture
    that does not support it, e.g. because it requires too many qubits or
    because the physical constraints on the geometry are not satisfied.
    """

    pass


class ExecutionError(Exception):
    """
    An error during the execution of a job.
    """

    pass


def make_sequence(program: QuantumProgram) -> pulser.Sequence:
    """
    Build a sequence for a device from a pulse and a register.

    This function is mostly intended for internal use and will likely move to qool-layer
    in time.

    Arguments:
        program: A quantum program to compile into a sequence.

    Raises:
        CompilationError if the pulse + register are not compatible with the device.
    """
    register = program.register
    if program.device.requires_layout and register.layout is None:
        register = program.register.with_automatic_layout(program.device)
    sequence = Sequence(register=register, device=program.device)
    sequence.declare_channel("rydberg_global", "rydberg_global")
    sequence.add(program.pulse, "rydberg_global")

    return sequence


class JobId(str):
    """
    A unique identifier for a job.
    """

    pass


@dataclass
class Result:
    """
    Low-level results returned from a backend.

    Specific backends may return subclasses of this class with additional
    backend-specific information.
    """

    counts: Counter[str]
    """
    A mapping from bitstrings observed to the number of instances of this
    bitstring observed.
    """

    def __len__(self) -> int:
        """
        The total number of measures.
        """
        return sum(self.counts.values())


@dataclass
class BaseJob(ABC):
    """
    A job, either pending or in progress.

    To wait until the job is complete, use `await job`.
    """

    id: JobId
    """
    The unique identifier for this job.

    You may save it to a database and use `Backend.proceed` to recreate
    a job from a JobId.
    """

    @abstractmethod
    def wait(self) -> Result:
        """
        Wait until the job is complete, blocking the entire thread until it is.

        Once the job is complete (or if it is already complete), return
        the result of the job. If the job failed, raise an ExecutionError.

        # Performance note

        This method is expected to spend most of its time outside the GIL, which
        means that if you run it on a background thread, it should not impact the
        performance of other threads.
        """
        ...

    @abstractmethod
    def status(self) -> BatchStatus:
        """
        Check the status of the job.

        This method is provided as a polling mechanism, mainly to help writing client
        code in libraries or applications that need to wait for the completion of numerous
        concurrent jobs. If you are simply interested in the result of a single job,
        you should rather use method `wait()`.
        """
        ...


class BaseBackend(ABC):
    """
    Base class for backends.

    # Implementation note

    If you implement a new backend, please:

    1. Make sure that `__init__` takes exactly the same arguments as
        `BaseBackend.__init__`.
    2. Register it as part of `BackendType`
    2. Make sure that it can be executed on a background thread.
    """

    def __init__(self, config: BackendConfig):
        self.config = config

    def default_number_of_runs(self) -> int:
        """
        A backend-specific reasonable default value for the number of runs.
        """
        # Reasonable default.
        return 100

    @abstractmethod
    def device(self) -> Device:
        """
        Specifications for the device picked by `BackendConfig.device`. If
        no such device was specified, return the default device for this
        backend.

        Note that any client (caller, etc.) MUST call `device()` to find out
        about the specific device, rather than instantiating a device directly
        from `pulser`. If your client ever calls a remote QPU, this is the
        ONLY way of being certain that you have access to the latest version
        of the QPU specs.

        # Performance note

        This method is expected to spend most of its time outside the GIL, which
        means that if you run it on a background thread, it should not impact the
        performance of other threads.
        """
        ...

    def run(self, program: QuantumProgram, runs: int | None = None) -> Result:
        """
        Submit a quantum program for execution and wait for its result.

        Arguments:
            runs: How many times the program must be executed on the backend.
                If `None`, pick a reasonable default.

        Note that if you are submitting a long job and expecting the need
        to resume it later, you should rather use `submit` and `proceed`.

        # Performance note

        This method is expected to spend most of its time outside the GIL, which
        means that if you run it on a background thread, it should not impact the
        performance of other threads.
        """
        return self.submit(program, runs).wait()

    @abstractmethod
    def submit(self, program: QuantumProgram, runs: int | None = None) -> BaseJob:
        """
        Submit a quantum program for execution.

        Arguments:
            runs: How many times the program must be executed on the backend.
                If `None`, pick a reasonable default.

                        Once a program is submitted, you can obtain a `BaseJob` from its job id
        by calling `proceed()`. This can be useful if you enqueue a program on a
        long queue (e.g. one in which you may need to wait for hours or days before
        you have access to a QPU), save the job id, turn off your computer, then
        resume your session a few days later to check the status of the program.

        # Performance note

        This method is expected to spend most of its time outside the GIL, which
        means that if you run it on a background thread, it should not impact the
        performance of other threads.
        """
        ...

    @abstractmethod
    def proceed(self, job: JobId) -> BaseJob:
        """
        Continue tracking execution of a quantum program submitted previously.

        This may be useful, for instance, if you have launched a remote quantum
        program during a previous session and now wish to check its result

        # Performance note

        This method is expected to spend most of its time outside the GIL, which
        means that if you run it on a background thread, it should not impact the
        performance of other threads.
        """
        ...


@dataclass
class JobSuccess(BaseJob):
    """
    A job that has already succeeded.
    """

    result: Result

    def status(self) -> BatchStatus:
        return BatchStatus.DONE

    def wait(self) -> Result:
        return self.result


@dataclass
class JobFailure(BaseJob):
    """
    A job that has already failed.
    """

    error: Exception

    def status(self) -> BatchStatus:
        return BatchStatus.ERROR

    def wait(self) -> Result:
        raise self.error


############################ Local backends


class BaseLocalBackend(BaseBackend):
    """
    Base class for emulators running locally.

    To implement a new local backend, you only need to provide an implementation
    of method `_execute_locally`.
    """

    def __init__(self, config: BackendConfig):
        super().__init__(config)
        device = config.device
        if device is None:
            device = pulser.AnalogDevice
        elif isinstance(device, NamedDevice):
            raise ValueError(
                "Local emulators do not support named devices, property `device` expects `None` "
                + "or a `DeviceType`"
            )
        elif isinstance(device, DeviceType):
            device = device.value
        assert isinstance(device, Device), f"Expected a device, got {device}"
        self._device = device

    def device(self) -> Device:
        return self._device

    def submit(self, program: QuantumProgram, runs: int | None = None) -> BaseJob:
        id = JobId(str(object=uuid4()))
        sequence = make_sequence(program)
        try:
            result = self._execute_locally(sequence, runs)
            return JobSuccess(id=id, result=result)
        except Exception as e:
            return JobFailure(id=id, error=e)

    @abstractmethod
    def _execute_locally(self, sequence: Sequence, runs: int | None = None) -> Result:
        """
        Execute a quantum program locally.

        Arguments:
            sequence: The Pulser sequence to execute.
            runs: The number of runs for the execution. If `None`, the backend should
                default to a reasonable number of runs.
        """
        ...

    def proceed(self, job: JobId) -> BaseJob:
        # FIXME: Implement save/restore job results.
        raise NotImplementedError()


class QutipBackend(BaseLocalBackend):
    """
    Execute a Register and a Pulse on the Qutip Emulator.

    Please consider using EmuMPSBackend, which generally works much better with
    higher number of qubits.

    Performance warning:
        Executing anything quantum related on an emulator takes an amount of resources
        polynomial in 2^N, where N is the number of qubits. This can easily go beyond
        the limit of the computer on which you're executing it.
    """

    def __init__(self, config: BackendConfig):
        super().__init__(config)

    def _execute_locally(self, sequence: Sequence, runs: int | None = None) -> Result:
        emulator = QutipEmulator.from_sequence(sequence)
        if runs is None:
            runs = 100  # Arbitrary device-specific value.
        result: Counter[str] = emulator.run().sample_final_state(N_samples=runs)
        return Result(counts=result)


if os.name == "posix":
    # EmuMPS is only available under Linux and Darwin/macOS.
    import emu_mps

    class EmuMPSBackend(BaseLocalBackend):
        """
        Execute a Register and a Pulse on the high-performance emu-mps Emulator.

        As of this writing, this local emulator is only available under Unix. However,
        the RemoteEmuMPSBackend is available on all platforms.

        Performance warning:
            Executing anything quantum related on an emulator takes an amount of resources
            polynomial in 2^N, where N is the number of qubits. This can easily go beyond
            the limit of the computer on which you're executing it.
        """

        def __init__(self, config: BackendConfig) -> None:
            super().__init__(config)

        def _execute_locally(
            self, sequence: Sequence, runs: int | None = None
        ) -> Result:
            times = [1.0]  # 1.0 = end of the duration (normalized)
            if runs is None:
                runs = 100  # Arbitrary device-specific value.
            bitstrings = emu_mps.BitStrings(evaluation_times=times, num_shots=runs)
            config = emu_mps.MPSConfig(observables=[bitstrings], dt=self.config.dt)
            backend = emu_mps.MPSBackend(sequence, config=config)
            results = backend.run()
            counter: Counter[str] = results.bitstrings[-1]
            return Result(counts=counter)

    import emu_sv

    # EmuSV is only available under Linux and Darwin/macOS.
    class EmuSVBackend(BaseLocalBackend):
        """
        Execute a Register and a Pulse on the high-performance emu-sv Emulator.

        As of this writing, this local emulator is only available under Unix.

        Performance warning:
            Executing anything quantum related on an emulator takes an amount of resources
            polynomial in 2^N, where N is the number of qubits. This can easily go beyond
            the limit of the computer on which you're executing it.
        """

        def __init__(self, config: BackendConfig) -> None:
            super().__init__(config)

        def _execute_locally(
            self, sequence: Sequence, runs: int | None = None
        ) -> Result:
            times = [1.0]  # 1.0 = end of the duration (normalized)
            if runs is None:
                runs = 100  # Arbitrary device-specific value.
            bitstrings = emu_sv.BitStrings(evaluation_times=times, num_shots=runs)
            config = emu_sv.SVConfig(
                dt=self.config.dt, observables=[bitstrings], log_level=0
            )
            backend = emu_sv.SVBackend(sequence, config=config)

            results = backend.run()
            counter: Counter[str] = results.get_result(bitstrings, time=1.0)
            return Result(counts=counter)


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
                self._error = Exception(
                    f"Error while executing remote job: {job.errors}"
                )
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
        """
        Make sure that we have fetched the latest specs for the device from the server.
        """
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
        """
        Enqueue execution of a Pulser sequence.
        """
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
            raise CompilationError(
                f"This register/pulse cannot be executed on the device: {e}"
            )
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
    A backend that uses a remote high-performance emulator (EmuMPS)
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


portable_backends_map: dict[BackendType, type[BaseBackend]] = {
    BackendType.QUTIP: cast(type[BaseBackend], QutipBackend),
    BackendType.REMOTE_EMUMPS: cast(type[BaseBackend], RemoteEmuMPSBackend),
    BackendType.REMOTE_QPU: cast(type[BaseBackend], RemoteQPUBackend),
    # FIXME: Implemente REMOTE_EMUFREE and REMOTE_EMUSV
}
"""
The backends available on all platforms.
"""

posix_backends_map: dict[BackendType, type[BaseBackend]] = {
    BackendType.EMU_MPS: cast(type[BaseBackend], EmuMPSBackend),
    BackendType.EMU_SV: cast(type[BaseBackend], EmuSVBackend),
}
"""
The backends available only on Posix platforms.
"""

if os.name == "posix":
    backends_map: dict[BackendType, type[BaseBackend]] = portable_backends_map.copy()
    for k, v in posix_backends_map.items():
        backends_map[k] = v
    unavailable_backends_map = {}
    """
    The backends not available on this platform.
    """
else:
    backends_map = portable_backends_map
    unavailable_backends_map = posix_backends_map


def get_backend(backend_config: BackendConfig) -> BaseBackend:
    """
    Instantiate a backend.

    # Concurrency note

    Backends are *not* meant to be shared across threads.
    """
    backend = backends_map.get(backend_config.backend, None)
    if backend is not None:
        return backend(backend_config)
    if backend_config.backend in unavailable_backends_map:
        raise ValueError(
            f"Backend {backend_config.backend} is not available on {os.name}."
        )
    else:
        raise ValueError(f"Unknown backend {backend_config.backend}.")
