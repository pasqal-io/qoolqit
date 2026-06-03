# waveforms collection

from __future__ import annotations

from .base_waveforms import CompositeWaveform, Waveform
from .utils import round_to_sum
from .waveforms import (
    Blackman,
    Constant,
    Delay,
    Interpolated,
    PiecewiseLinear,
    Ramp,
    Sin,
)

__all__ = [
    "Waveform",
    "CompositeWaveform",
    "Constant",
    "Delay",
    "PiecewiseLinear",
    "Ramp",
    "Sin",
    "Blackman",
    "Interpolated",
    "round_to_sum",
]