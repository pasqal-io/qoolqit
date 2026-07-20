from __future__ import annotations

import pytest

import qoolqit
from qoolqit.waveforms import (
    BlackmanWaveform,
    ConstantWaveform,
    DelayWaveform,
    InterpolatedWaveform,
    PiecewiseLinearWaveform,
    RampWaveform,
)


@pytest.mark.parametrize(
    "deprecated_name, expected_type",
    [
        ("Blackman", BlackmanWaveform),
        ("Constant", ConstantWaveform),
        ("Delay", DelayWaveform),
        ("Interpolated", InterpolatedWaveform),
        ("PiecewiseLinear", PiecewiseLinearWaveform),
        ("Ramp", RampWaveform),
    ],
)
def test_waveforms_deprecation_warning(deprecated_name: str, expected_type: type) -> None:
    with pytest.warns(DeprecationWarning, match=f"{deprecated_name} is deprecated"):
        cls = getattr(qoolqit, deprecated_name)
        assert cls is expected_type
