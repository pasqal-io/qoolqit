from __future__ import annotations

from importlib import import_module

from .devices import *
from .graphs import *
from .quantum_program import *
from .register import *
from .sequence import *
from .waveforms import *

list_of_submodules = [
    ".graphs",
    ".sequence",
    ".devices",
    ".waveforms",
    ".register",
    ".quantum_program",
]

__all__ = []
for submodule in list_of_submodules:
    __all_submodule__ = getattr(import_module(submodule, package="qoolqit"), "__all__")
    __all__ += __all_submodule__
