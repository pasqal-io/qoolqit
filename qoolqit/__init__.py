"""A Python library for algorithm development in the Rydberg Analog Model."""

from __future__ import annotations

from pulser.sequence import store_package_version_metadata

from qoolqit.devices import (
    AnalogDevice,
    Device,
    DigitalAnalogDevice,
    MockDevice,
    available_default_devices,
)
from qoolqit.drive import Drive
from qoolqit.execution import SequenceCompiler
from qoolqit.graphs import DataGraph
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import Blackman, Constant, Delay, Interpolated, PiecewiseLinear, Ramp, Sin

__all__ = [
    "DataGraph",
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
    "SequenceCompiler",
    "available_default_devices",
    "AnalogDevice",
    "DigitalAnalogDevice",
    "MockDevice",
    "Device",
]


__version__ = "1.0.0"

store_package_version_metadata("qoolqit", __version__)
