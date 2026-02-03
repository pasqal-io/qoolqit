"""A Python library for algorithm development in the Rydberg Analog Model."""

from __future__ import annotations

import pulser
from packaging.version import Version

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
from qoolqit.waveforms import Blackman, Constant, Delay, Interpolated, PiecewiseLinear, Ramp, Sin

__all__ = [
    "DataGraph",
    "InteractionEmbedder",
    "InteractionEmbeddingConfig",
    "SpringLayoutConfig",
    "SpringLayoutEmbedder",
    "Blackman",
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

# metadata are stored only from pulser 1.6.3
pulser_version = Version(pulser.__version__)
if pulser_version >= Version("1.6.3"):
    from pulser.sequence import store_package_version_metadata

    store_package_version_metadata("qoolqit", __version__)
