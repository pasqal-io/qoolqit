# waveforms collection

from __future__ import annotations

from waveforms.base_waveforms import Waveform, CompositeWaveform
from waveforms.waveforms import (
    Constant,
    Delay,
    PiecewiseLinear,
    Ramp,
    Sine,
    Blackman,
    Interpolated,
)

from waveforms.utils import round_to_sum