from __future__ import annotations

import logging
import os
from typing import cast

from qoolqit._solvers.types import BackendType

from .base_backend import BackendConfig, BaseBackend
from .local_backends import QutipBackend
from .remote_backends import (
    RemoteEmuFREEBackend,
    RemoteEmuMPSBackend,
    RemoteEmuTNBackend,
    RemoteQPUBackend,
)

logger = logging.getLogger(__name__)


portable_backends_map: dict[BackendType, type[BaseBackend]] = {
    BackendType.QUTIP: cast(type[BaseBackend], QutipBackend),
    BackendType.REMOTE_EMUMPS: cast(type[BaseBackend], RemoteEmuMPSBackend),
    BackendType.REMOTE_QPU: cast(type[BaseBackend], RemoteQPUBackend),
    BackendType.REMOTE_EMUFREE: cast(type[BaseBackend], RemoteEmuFREEBackend),
    BackendType.REMOTE_EMUTN: cast(type[BaseBackend], RemoteEmuTNBackend),
}
"""The backends available on all platforms."""

if os.name == "posix":
    from .local_backends import EmuMPSBackend, EmuSVBackend

    posix_backends_map: dict[BackendType, type[BaseBackend]] = {
        BackendType.EMU_MPS: cast(type[BaseBackend], EmuMPSBackend),
        BackendType.EMU_SV: cast(type[BaseBackend], EmuSVBackend),
    }
    """The backends available only on Posix platforms."""
    backends_map: dict[BackendType, type[BaseBackend]] = portable_backends_map.copy()
    for k, v in posix_backends_map.items():
        backends_map[k] = v
    unavailable_backends_map = {}
    """The backends not available on this platform."""
else:
    backends_map = portable_backends_map
    unavailable_backends_map = {
        BackendType.EMU_MPS: cast(type[BaseBackend], None),
        BackendType.EMU_SV: cast(type[BaseBackend], None),
    }


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
        raise ValueError(f"Backend {backend_config.backend} is not available on {os.name}.")
    else:
        raise ValueError(f"Unknown backend {backend_config.backend}.")
