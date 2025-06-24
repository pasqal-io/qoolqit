from __future__ import annotations

import os

from .base_backend import BaseBackend
from .get_backend import get_backend
from .local_backends import BaseLocalBackend, QutipBackend
from .remote_backends import (
    BaseRemoteBackend,
    RemoteEmuFREEBackend,
    RemoteEmuMPSBackend,
    RemoteEmuTNBackend,
    RemoteJob,
    RemoteQPUBackend,
)

__all__ = [
    "BaseBackend",
    "BaseLocalBackend",
    "BaseRemoteBackend",
    "QutipBackend",
    "RemoteQPUBackend",
    "RemoteEmuMPSBackend",
    "RemoteEmuTNBackend",
    "RemoteEmuFREEBackend",
    "get_backend",
    "RemoteJob",
]

if os.name == "posix":
    from .local_backends import EmuMPSBackend, EmuSVBackend

    __all__ += [
        "EmuMPSBackend",
        "EmuSVBackend",
    ]
