from __future__ import annotations

from random import uniform
from typing import Callable, Generator

import numpy as np
import pytest

from qoolqit.drive import Drive, WeightedDetuning
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import Ramp, Waveform


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
def random_waveform_factory() -> (
    Callable[[float, float, float, int | np.random.Generator], Waveform]
):
    def _create_random_waveform(
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

    return _create_random_waveform


@pytest.fixture
def dmm_program(
    random_linear_register_factory: Callable[[float, int | np.random.Generator], Register],
) -> Generator[Callable[[], QuantumProgram]]:
    def _generate_program() -> QuantumProgram:
        rng = np.random.default_rng()
        register = random_linear_register_factory(1.0, rng)
        wf_amp = Ramp(1.0, 0.5, 0.5)
        wf_det = Ramp(1.0, -0.2, -0.5)
        wdetuning = WeightedDetuning(
            weights={q: uniform(0.1, 0.99) for q in register.qubits_ids},
            waveform=wf_det,
        )
        drive = Drive(amplitude=wf_amp, detuning=wf_det, weighted_detunings=[wdetuning])
        return QuantumProgram(register, drive)

    yield _generate_program
