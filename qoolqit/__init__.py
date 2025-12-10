"""A Python library for algorithm development in the Rydberg Analog Model."""

from __future__ import annotations

from pulser.sequence import store_package_version_metadata

from qoolqit.devices import AnalogDevice, DigitalAnalogDevice, MockDevice
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
from qoolqit.waveforms import Constant, Delay, Interpolated, PiecewiseLinear, Ramp, Sin

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
    "Sin",
    "Drive",
    "Register",
    "QuantumProgram",
    "CompilerProfile",
    "SequenceCompiler",
    "AnalogDevice",
    "DigitalAnalogDevice",
    "MockDevice",
]


__version__ = "0.3.1"
store_package_version_metadata(package_name="qoolqit", package_version=__version__)
