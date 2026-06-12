"""A Python library for algorithm development in the Rydberg Analog Model."""

from __future__ import annotations

import warnings

from pulser.sequence import store_package_version_metadata

from qoolqit.devices import (
    AnalogDevice,
    AnalogDeviceWithDMM,
    Device,
    DigitalAnalogDevice,
    MockDevice,
    available_default_devices,
)
from qoolqit.drive import Drive
from qoolqit.execution.sequence_compiler import SequenceCompiler
from qoolqit.graphs import DataGraph
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import (
    BlackmanWaveform,
    ConstantWaveform,
    DelayWaveform,
    InterpolatedWaveform,
    PiecewiseLinearWaveform,
    RampWaveform,
    SinWaveform,
)

__all__ = [
    "DataGraph",
    "BlackmanWaveform",
    "ConstantWaveform",
    "DelayWaveform",
    "InterpolatedWaveform",
    "PiecewiseLinearWaveform",
    "RampWaveform",
    "SinWaveform",
    "Drive",
    "Register",
    "QuantumProgram",
    "SequenceCompiler",
    "available_default_devices",
    "AnalogDevice",
    "AnalogDeviceWithDMM",
    "DigitalAnalogDevice",
    "MockDevice",
    "Device",
    # Deprecated short-form aliases (e.g. "Blackman", "Constant", ...) are intentionally
    # excluded from __all__. They are handled dynamically via __getattr__ below so that
    # they do not appear in auto-complete or wildcard imports, discouraging new usage.
]


__version__ = "1.1.1"

store_package_version_metadata("qoolqit", __version__)


# ---------------------------------------------------------------------------
# Deprecated aliases — will be removed in a future release.
# ---------------------------------------------------------------------------

_DEPRECATED_WAVEFORM_ALIASES: dict[str, type] = {
    "Blackman": BlackmanWaveform,
    "Constant": ConstantWaveform,
    "Delay": DelayWaveform,
    "Interpolated": InterpolatedWaveform,
    "PiecewiseLinear": PiecewiseLinearWaveform,
    "Ramp": RampWaveform,
    "Sin": SinWaveform,
}


def __getattr__(name: str) -> type:
    # No else condition since Python only calls __getattr__ on a module
    # when the normal lookup has already failed.
    if name in _DEPRECATED_WAVEFORM_ALIASES:
        new_name = _DEPRECATED_WAVEFORM_ALIASES[name]
        warnings.warn(
            f"{name} is deprecated and will be removed in v1.4. "
            f"Use the equivalent {new_name.__name__} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return new_name
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
