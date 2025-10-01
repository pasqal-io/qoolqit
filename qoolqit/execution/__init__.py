from __future__ import annotations

import os

from .backend import QutipBackend
from .backends import QPU, Emulator, RemoteEmulator
from .sequence_compiler import SequenceCompiler
from .utils import BackendName, CompilerProfile, ResultType

__all__ = [
    "SequenceCompiler",
    "CompilerProfile",
    "ResultType",
    "BackendName",
    "QutipBackend",
    "Emulator",
    "RemoteEmulator",
    "QPU",
]

if os.name == "posix":
    from .backend import EmuMPSBackend

    __all__ += ["EmuMPSBackend"]
