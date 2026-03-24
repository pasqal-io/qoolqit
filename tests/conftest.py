from __future__ import annotations

from random import randint, uniform
from typing import Callable, Generator

import numpy as np
import pytest

from qoolqit.drive import Drive, WeightedDetuning
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import Ramp, Waveform

# from numpy.random import RandomState, Generator


@pytest.fixture
def random_pos_ramp() -> Generator[Callable[[], Waveform]]:
    def _generate_random_waveform() -> Waveform:
        n = randint(2, 6)
        wf: Waveform = Ramp(uniform(0.1, 1.0), uniform(0.0, 1.0), uniform(0.0, 1.0))
        for _ in range(n):
            wf = wf >> Ramp(uniform(0.1, 1.0), uniform(0.0, 1.0), uniform(0.0, 1.0))
        return wf

    yield _generate_random_waveform


@pytest.fixture
def random_neg_ramp() -> Generator[Callable[[], Waveform]]:
    def _generate_random_waveform() -> Waveform:
        n = randint(2, 6)
        wf: Waveform = Ramp(uniform(0.1, 1.0), uniform(-1.0, 1.0), uniform(-1.0, 1.0))
        while wf.min() >= 0:
            for _ in range(n):
                wf = wf >> Ramp(uniform(0.1, 1.0), uniform(-1.0, 1.0), uniform(-1.0, 1.0))
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
def random_linear_register_factory() -> Callable[[float, int | np.random.Generator], Register]:
    def _generate_random_linear_register(
        min_distance: float, seed: int | np.random.Generator = np.random.default_rng()
    ) -> Register:
        rng = np.random.default_rng(seed)
        n = rng.integers(low=2, high=5)
        start_x = -(n - 1) / 2.0
        coords = [((start_x + i) * min_distance, 0.0) for i in range(n)]
        return Register.from_coordinates(coords)

    return _generate_random_linear_register


@pytest.fixture
def random_program(
    random_linear_register: Callable[[], Register], random_drive: Callable[[], Drive]
) -> Generator[Callable[[], QuantumProgram]]:
    def _generate_random_program() -> QuantumProgram:
        register = random_linear_register()
        drive = random_drive()
        return QuantumProgram(register, drive)

    yield _generate_random_program


@pytest.fixture
def dmm_program(
    random_linear_register: Callable[[], Register],
) -> Generator[Callable[[], QuantumProgram]]:
    def _generate_program() -> QuantumProgram:
        register = random_linear_register()
        wf_amp = Ramp(1.0, 0.5, 0.5)
        wf_det = Ramp(1.0, -0.2, -0.5)
        wdetuning = WeightedDetuning(
            weights={q: uniform(0.1, 0.99) for q in register.qubits_ids},
            waveform=wf_det,
        )
        drive = Drive(amplitude=wf_amp, detuning=wf_det, weighted_detunings=[wdetuning])
        return QuantumProgram(register, drive)

    yield _generate_program


@pytest.fixture
def random_amplitude_factory() -> (
    Callable[[float, float, float, int | np.random.Generator], Waveform]
):
    def _create_random_amplitude(
        min_value: float,
        max_value: float,
        max_duration: float,
        seed: int | np.random.Generator = np.random.default_rng(),
    ) -> Waveform:
        rng = np.random.default_rng(seed)
        n = rng.integers(2, 5)
        durations = rng.uniform(1.0, 2.0, size=n)
        durations *= rng.uniform(max_duration / 100, max_duration) / np.sum(durations)
        wf: Waveform = Ramp(
            durations[0],
            initial_value=rng.uniform(min_value, max_value),
            final_value=rng.uniform(min_value, max_value),
        )
        for i in range(1, n):
            wf = wf >> Ramp(
                durations[i],
                initial_value=rng.uniform(min_value, max_value),
                final_value=rng.uniform(min_value, max_value),
            )
        return wf

    return _create_random_amplitude
