from __future__ import annotations

from random import randint, uniform
from typing import Callable, Generator

import pytest

from qoolqit.drive import Drive
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import Ramp, Waveform


@pytest.fixture
def random_pos_ramp() -> Generator[Callable[[], Waveform]]:
    def _generate_random_waveform() -> Waveform:
        n = randint(2, 6)
        wf: Waveform = Ramp(uniform(0.5, 1.0), uniform(0.0, 1.0), uniform(0.0, 1.0))
        for _ in range(n):
            wf = wf >> Ramp(uniform(0.5, 1.0), uniform(0.0, 1.0), uniform(0.0, 1.0))
        return wf

    yield _generate_random_waveform


@pytest.fixture
def random_neg_ramp() -> Generator[Callable[[], Waveform]]:
    def _generate_random_waveform() -> Waveform:
        n = randint(2, 6)
        wf: Waveform = Ramp(uniform(0.5, 1.0), uniform(-1.0, 1.0), uniform(-1.0, 1.0))
        while wf.min() >= 0:
            for _ in range(n):
                wf = wf >> Ramp(uniform(0.5, 1.0), uniform(-1.0, 1.0), uniform(-1.0, 1.0))
        return wf

    yield _generate_random_waveform


@pytest.fixture
def random_drive(
    random_pos_ramp: Callable[[], Waveform], random_neg_ramp: Callable[[], Waveform]
) -> Generator[Callable[[], Drive]]:
    def _generate_random_drive() -> Drive:
        wf_amp = random_pos_ramp()
        wf_det = random_neg_ramp()
        return Drive(amplitude=wf_amp, detuning=wf_det)

    yield _generate_random_drive


@pytest.fixture
def random_linear_register() -> Generator[Callable[[], Register]]:
    def _generate_random_register() -> Register:
        n = randint(2, 5)
        start_x = -(n - 1) / 2.0
        coords = [(start_x + i, 0.0) for i in range(n)]
        return Register.from_coordinates(coords)

    yield _generate_random_register


@pytest.fixture
def random_program(
    random_linear_register: Callable[[], Register], random_drive: Callable[[], Drive]
) -> Generator[Callable[[], QuantumProgram]]:
    def _generate_random_program() -> QuantumProgram:
        register = random_linear_register()
        drive = random_drive()
        return QuantumProgram(register, drive)

    yield _generate_random_program
