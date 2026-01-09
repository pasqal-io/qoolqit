"""A Python library for algorithm development in the Rydberg Analog Model."""

from __future__ import annotations

import pulser.sequence as pulser_sequence

from qoolqit.devices import (
    AnalogDevice,
    Device,
    DigitalAnalogDevice,
    MockDevice,
    available_default_devices,
)
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
    "available_default_devices",
    "AnalogDevice",
    "DigitalAnalogDevice",
    "MockDevice",
    "Device",
]


__version__ = "0.3.3"

if hasattr(pulser_sequence, "store_package_version_metadata"):
    pulser_sequence.store_package_version_metadata("qoolqit", __version__)
