# qubosolver/_qoolkit/__init__.py

from __future__ import annotations

import os

from qoolqit._solvers.types import DeviceType

from .backends import (
    BackendConfig,
    BackendType,
    BaseJob,
    BaseLocalBackend,
    BaseRemoteBackend,
    CompilationError,
    ExecutionError,
    JobId,
    QuantumProgram,
    QutipBackend,
    RemoteEmuMPSBackend,
    Result,
    get_backend,
)

__all__ = [
    "BackendConfig",
    "BackendType",
    "BaseJob",
    "BaseLocalBackend",
    "BaseRemoteBackend",
    "CompilationError",
    "ExecutionError",
    "JobId",
    "QuantumProgram",
    "QutipBackend",
    "RemoteEmuMPSBackend",
    "Result",
    "get_backend",
    "DeviceType",
]

if os.name == "posix":
    from .backends import EmuMPSBackend, EmuSVBackend

    __all__ += [
        "EmuMPSBackend",
        "EmuSVBackend",
    ]
