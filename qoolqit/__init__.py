"""A Python library for algorithm development in the Rydberg Analog Model."""

from __future__ import annotations

from importlib import import_module
import warnings

try:
    import torch
except ImportError:
    torch = None
else:
    # If CUDA is not available - avoid NVML warning
    if not torch.cuda.is_available():
        warnings.filterwarnings(
            "ignore",
            message="Can't initialize NVML"
        )

from qoolqit.graphs import DataGraph

from .devices import *
from .drive import *
from .embedding import *
from .execution import *
from .program import *
from .register import *
from .waveforms import *

list_of_submodules = [
    ".drive",
    ".devices",
    ".waveforms",
    ".register",
    ".program",
    ".execution",
    ".embedding",
]

__all__ = ["DataGraph"]
for submodule in list_of_submodules:
    __all_submodule__ = getattr(import_module(submodule, package="qoolqit"), "__all__")
    __all__ += __all_submodule__

__version__ = "0.3.1"
