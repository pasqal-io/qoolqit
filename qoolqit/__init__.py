from __future__ import annotations

from importlib import import_module

from .devices import *
from .drive import *
from .embedding import *
from .execution import *
from .graphs import *
from .program import *
from .register import *
from .waveforms import *

list_of_submodules = [
    ".graphs",
    ".drive",
    ".devices",
    ".waveforms",
    ".register",
    ".program",
    ".execution",
    ".embedding",
]

__all__ = []
for submodule in list_of_submodules:
    __all_submodule__ = getattr(import_module(submodule, package="qoolqit"), "__all__")
    __all__ += __all_submodule__
