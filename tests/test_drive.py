from __future__ import annotations

import random

import pytest

from qoolqit.drive import Drive
from qoolqit.waveforms import Delay, Ramp


def test_drive_init_and_composition() -> None:

    duration_amp = 10.0 * random.random()
    duration_det = 10.0 * random.random()

    amp_wf = Ramp(duration_amp, random.random(), random.random())
    det_wf = Ramp(duration_det, -random.random(), random.random())

    with pytest.raises(TypeError):
        drive = Drive(amp_wf)

    with pytest.raises(ValueError):
        drive = Drive()

    with pytest.raises(TypeError):
        drive = Drive(amplitude=1.0, detuning=det_wf)  # type: ignore [arg-type]

    with pytest.raises(TypeError):
        drive = Drive(amplitude=amp_wf, detuning=1.0)  # type: ignore [arg-type]

    with pytest.raises(ValueError):
        drive = Drive(amplitude=det_wf)

    drive = Drive(amplitude=amp_wf, detuning=det_wf)

    assert drive.duration == max([duration_amp, duration_det])

    drive = drive >> drive
    assert drive.duration == 2.0 * max([duration_amp, duration_det])

    drive = drive >> drive
    assert drive.duration == 4.0 * max([duration_amp, duration_det])

    drive = Drive(amplitude=amp_wf)
    assert isinstance(drive.detuning, Delay)
    assert drive.duration == duration_amp

    drive = Drive(detuning=det_wf)
    assert isinstance(drive.amplitude, Delay)
    assert drive.duration == duration_det

    phase = random.random()
    drive1 = Drive(amplitude=amp_wf, detuning=det_wf, phase=phase)
    drive2 = Drive(amplitude=amp_wf, detuning=det_wf, phase=phase)
    drive = drive1 >> drive2
    assert drive.phase == phase

    with pytest.raises(NotImplementedError):
        drive1 = Drive(amplitude=amp_wf, detuning=det_wf, phase=1.0)
        drive2 = Drive(amplitude=amp_wf, detuning=det_wf, phase=0.0)
        drive1 >> drive2
