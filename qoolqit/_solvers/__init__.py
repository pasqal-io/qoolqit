from __future__ import annotations

import os

from qoolqit._solvers.types import DeviceType

from .backends.base_backend import (
    BackendConfig,
    BaseBackend,
    BaseJob,
    JobId,
    QuantumProgram,
    Result,
)
from .backends.get_backend import get_backend
from .backends.local_backends import BaseLocalBackend, QutipBackend
from .backends.remote_backends import RemoteEmuMPSBackend, RemoteJob, RemoteQPUBackend
from .data import BackendType, CompilationError, ExecutionError

__all__ = [
    "BackendConfig",
    "BaseBackend",
    "BackendType",
    "BaseJob",
    "BaseLocalBackend",
    "BaseRemoteBackend",
    "CompilationError",
    "ExecutionError",
    "JobId",
    "QuantumProgram",
    "QutipBackend",
    "RemoteQPUBackend",
    "RemoteEmuMPSBackend",
    "Result",
    "get_backend",
    "RemoteJob",
    "DeviceType",
]

if os.name == "posix":
    from .backends.local_backends import EmuMPSBackend, EmuSVBackend

    __all__ += [
        "EmuMPSBackend",
        "EmuSVBackend",
    ]
