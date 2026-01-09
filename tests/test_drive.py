from __future__ import annotations

import math
import random
from typing import Callable

import pytest

from qoolqit.drive import Drive, WeightedDetuning
from qoolqit.utils import EQUAL
from qoolqit.waveforms import Delay, Ramp, Waveform


def test_drive_init_and_composition(
    random_pos_ramp: Callable[[], Waveform], random_neg_ramp: Callable[[], Waveform]
) -> None:

    amp_wf = random_pos_ramp()
    det_wf = random_neg_ramp()

    duration_amp = amp_wf.duration
    duration_det = det_wf.duration

    with pytest.raises(TypeError):
        drive = Drive(amp_wf)

    with pytest.raises(ValueError):
        drive = Drive()

    with pytest.raises(TypeError, match="Amplitude and detuning must be of type Waveform."):
        drive = Drive(amplitude=1.0, detuning=det_wf)  # type: ignore [arg-type]

    with pytest.raises(TypeError, match="Amplitude and detuning must be of type Waveform."):
        drive = Drive(amplitude=amp_wf, detuning=1.0)  # type: ignore [arg-type]

    with pytest.raises(ValueError):
        drive = Drive(amplitude=det_wf)

    drive = Drive(amplitude=amp_wf, detuning=det_wf)

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


def test_error_wdetuning_positive() -> None:
    with pytest.raises(ValueError):
        WeightedDetuning(weights={0: 1}, waveform=Ramp(1.0, 0.2, 0.5))
