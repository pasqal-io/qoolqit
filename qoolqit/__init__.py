"""A Python library for algorithm development in the Rydberg Analog Model."""

from __future__ import annotations

from importlib import import_module

from qoolqit.drive import Drive
from qoolqit.embedding import (
    InteractionEmbedder,
    InteractionEmbeddingConfig,
    SpringLayoutConfig,
    SpringLayoutEmbedder,
)
from qoolqit.execution import CompilerProfile, SequenceCompiler
from qoolqit.graphs import DataGraph
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import Constant, Delay, Interpolated, PiecewiseLinear, Ramp

from .devices import *

list_of_submodules = [
    ".devices",
]

__all__ = [
    "DataGraph",
    "InteractionEmbedder",
    "InteractionEmbeddingConfig",
    "SpringLayoutConfig",
    "SpringLayoutEmbedder",
    "Constant",
    "Delay",
    "Interpolated",
    "PiecewiseLinear",
    "Ramp",
    "Drive",
    "Register",
    "QuantumProgram",
    "CompilerProfile",
    "SequenceCompiler",
]

for submodule in list_of_submodules:
    __all_submodule__ = getattr(import_module(submodule, package="qoolqit"), "__all__")
    __all__ += __all_submodule__

__version__ = "0.3.1"
