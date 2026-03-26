from __future__ import annotations

import math
import random

import pytest

from qoolqit.drive import Drive, WeightedDetuning
from qoolqit.utils import EQUAL
from qoolqit.waveforms import Constant, Delay, PiecewiseLinear, Ramp
from qoolqit.waveforms.base_waveforms import Waveform


@pytest.mark.parametrize(
    "amp_wf, det_wf",
    [
        (Ramp(10.0, 1.0, 0.0), Ramp(12.1, -2.1, 2.1)),
        (
            Constant(10.0, math.pi),
            PiecewiseLinear(
                [4.60132814, 4.18237748, 5.21984795, 3.5963718],
                [0.1443786, -0.2027756, 0.46146151, 0.07375925, 0.52915184],
            ),
        ),
    ],
)
def test_drive_init_and_composition(amp_wf: Waveform, det_wf: Waveform) -> None:

    with pytest.raises(ValueError):
        drive = Drive()

    with pytest.raises(TypeError):
        drive = Drive(amp_wf)

    with pytest.raises(TypeError, match="Amplitude and detuning must be of type Waveform."):
        drive = Drive(amplitude=1.0, detuning=det_wf)  # type: ignore [arg-type]

    with pytest.raises(TypeError, match="Amplitude and detuning must be of type Waveform."):
        drive = Drive(amplitude=amp_wf, detuning=1.0)  # type: ignore [arg-type]

    with pytest.raises(ValueError):
        drive = Drive(amplitude=det_wf)

    drive = Drive(amplitude=amp_wf, detuning=det_wf)

    duration_amp = amp_wf.duration
    duration_det = det_wf.duration

    assert math.isclose(drive.duration, max([duration_amp, duration_det]))

    drive = drive >> drive
    assert EQUAL(drive.duration, 2.0 * max([duration_amp, duration_det]))

    drive = drive >> drive
    assert EQUAL(drive.duration, 4.0 * max([duration_amp, duration_det]))

    drive = Drive(amplitude=amp_wf)
    assert isinstance(drive.detuning, Delay)
    assert EQUAL(drive.duration, duration_amp)

    drive = Drive(detuning=det_wf)
    assert isinstance(drive.amplitude, Delay)
    assert EQUAL(drive.duration, duration_det)

    drive = Drive(
        detuning=det_wf,
        weighted_detunings=[WeightedDetuning(weights={0: 1}, waveform=Ramp(1.0, -0.2, -0.5))],
    )
    assert len(drive.weighted_detunings) == 1
    assert EQUAL(drive.duration, duration_det)

    phase = random.random()
    drive1 = Drive(amplitude=amp_wf, detuning=det_wf, phase=phase)
    drive2 = Drive(amplitude=amp_wf, detuning=det_wf, phase=phase)
    drive = drive1 >> drive2
    assert EQUAL(drive.phase, phase)

    with pytest.raises(NotImplementedError):
        drive1 = Drive(amplitude=amp_wf, detuning=det_wf, phase=1.0)
        drive2 = Drive(amplitude=amp_wf, detuning=det_wf, phase=0.0)
        drive1 >> drive2


def test_error_amplitude_negative() -> None:
    with pytest.raises(ValueError, match="Amplitude cannot be negative."):
        neg_ramp = Ramp(10.0, -1.0, 2.0)
        Drive(amplitude=neg_ramp, detuning=neg_ramp)


def test_error_weighted_detuning_positive() -> None:
    with pytest.raises(ValueError):
        WeightedDetuning(weights={0: 1}, waveform=Ramp(1.0, 0.2, 0.5))


@pytest.mark.parametrize("amp_duration, det_duration", [(1.0, 1.005), (20.0, 10.0)])
def test_drive_duration_with_delays(amp_duration: float, det_duration: float) -> None:
    amp_wf = Ramp(amp_duration, 1.0, 0.0)
    det_wf = Ramp(det_duration, -1.0, 0.0)
    drive = Drive(amplitude=amp_wf, detuning=det_wf)
    assert drive.duration == max(amp_duration, det_duration)
