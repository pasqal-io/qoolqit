from __future__ import annotations

import math
import random

import pytest

from qoolqit.drive import DetuningMapModulator, Drive
from qoolqit.waveforms import Constant, Delay, PiecewiseLinear, Ramp, Waveform


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

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'amplitude'"):
        Drive()  # type: ignore [call-arg]

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'amplitude'"):
        Drive(detuning=Constant(duration=10, value=1.0))  # type: ignore [call-arg]

    with pytest.raises(TypeError, match="'amplitude' and 'detuning' must be of type Waveform."):
        drive = Drive(amplitude=1.0, detuning=det_wf)  # type: ignore [arg-type]

    with pytest.raises(TypeError, match="'amplitude' and 'detuning' must be of type Waveform."):
        drive = Drive(amplitude=amp_wf, detuning=1.0)  # type: ignore [arg-type]

    with pytest.raises(ValueError, match="'amplitude' must be positive."):
        drive = Drive(amplitude=det_wf)

    drive = Drive(amplitude=amp_wf, detuning=det_wf)

    with pytest.raises(
        NotImplementedError, match="Composing with object of type <class 'float'> not supported."
    ):
        drive >> 1.0  # type: ignore [operator]

    duration_amp = amp_wf.duration
    duration_det = det_wf.duration

    assert math.isclose(drive.duration, max([duration_amp, duration_det]))

    drive = drive >> drive
    assert math.isclose(drive.duration, 2.0 * max([duration_amp, duration_det]))

    drive = drive >> drive
    assert math.isclose(drive.duration, 4.0 * max([duration_amp, duration_det]))

    drive = Drive(amplitude=amp_wf)
    assert isinstance(drive.detuning, Delay)
    assert math.isclose(drive.duration, duration_amp)

    phase = random.random()
    drive_rand_phase = Drive(amplitude=amp_wf, detuning=det_wf, phase=phase)
    drive = drive_rand_phase >> drive_rand_phase
    assert math.isclose(drive.phase, phase)

    with pytest.raises(NotImplementedError):
        drive1 = Drive(amplitude=amp_wf, detuning=det_wf, phase=1.0)
        drive2 = Drive(amplitude=amp_wf, detuning=det_wf, phase=0.0)
        drive = drive1 >> drive2


def test_error_amplitude_negative() -> None:
    with pytest.raises(ValueError, match="'amplitude' must be positive."):
        neg_ramp = Ramp(10.0, -1.0, 2.0)
        Drive(amplitude=neg_ramp, detuning=neg_ramp)


@pytest.mark.parametrize("amp_duration, det_duration", [(1.0, 1.005), (20.0, 10.0)])
def test_drive_duration_with_delays(amp_duration: float, det_duration: float) -> None:
    amp_wf = Ramp(amp_duration, 1.0, 0.0)
    det_wf = Ramp(det_duration, -1.0, 0.0)
    drive = Drive(amplitude=amp_wf, detuning=det_wf)
    assert drive.duration == max(amp_duration, det_duration)


def test_dmm_init() -> None:
    positive_wf = Ramp(10.0, -10.0, 1.0)
    negative_wf = Ramp(10.0, -1.0, -2.0)

    valid_weights = {0: 0.1, 1: 0.2, 2: 0.3}
    invalid_weights = {0: 1.1, 1: 0.3}

    with pytest.raises(ValueError, match="`weights` must be a dictionary of values in \\[0, 1\\]."):
        DetuningMapModulator(negative_wf, weights=invalid_weights)

    with pytest.raises(ValueError, match="`waveform` must be negative for all times."):
        DetuningMapModulator(positive_wf, weights=valid_weights)

    dmm = DetuningMapModulator(negative_wf, weights=valid_weights)
    assert isinstance(dmm.waveform, Ramp)
    assert dmm.weights == valid_weights
