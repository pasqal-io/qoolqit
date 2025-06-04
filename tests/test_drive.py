from __future__ import annotations

import random

import pytest

from qoolqit.drive import Drive
from qoolqit.waveforms import Ramp


def test_drive() -> None:

    wf = Ramp(1.0, random.random(), random.random())

    with pytest.raises(TypeError):
        drive = Drive(wf)

    with pytest.raises(ValueError):
        drive = Drive()

    with pytest.raises(TypeError):
        drive = Drive(amplitude=1.0, detuning=wf)  # type: ignore [arg-type]

    with pytest.raises(TypeError):
        drive = Drive(amplitude=wf, detuning=1.0)  # type: ignore [arg-type]
