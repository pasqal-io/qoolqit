from __future__ import annotations

from functools import reduce
from math import pi
from random import randint, uniform
from typing import Callable, Generator

import numpy as np
import pytest
from scipy.linalg import expm

from qoolqit.drive import Drive, WeightedDetuning
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


@pytest.fixture
def random_program_dmm(
    random_linear_register: Callable[[], Register],
    random_pos_ramp: Callable[[], Waveform],
    random_neg_ramp: Callable[[], Waveform],
) -> Generator[Callable[[], QuantumProgram]]:
    def _generate_random_program() -> QuantumProgram:
        register = random_linear_register()
        wf_amp = random_pos_ramp()
        wf_det = random_neg_ramp()
        wdetuning = WeightedDetuning(
            weights={q: uniform(0.1, 0.99) for q in register.qubits.keys()},
            waveform=Ramp(1.0, -0.2, -0.5),
        )
        drive = Drive(amplitude=wf_amp, detuning=wf_det, weighted_detunings=[wdetuning])
        return QuantumProgram(register, drive)

    yield _generate_random_program


@pytest.fixture
def random_n_qubits() -> int:
    return randint(1, 8)


@pytest.fixture
def random_rotation_angle() -> float:
    return uniform(0, 1) * pi


@pytest.fixture
def evaluation_times() -> list[float]:
    return list(np.linspace(0, 1, 101))


@pytest.fixture
def random_x_rotation(random_n_qubits: int, random_rotation_angle: float) -> np.ndarray:
    # Pauli-X and identity matrices
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    id_mat = np.eye(2, dtype=complex)

    # Build Hamiltonian H = sum_j X_j
    dim = 2**random_n_qubits
    H = np.zeros((dim, dim), dtype=complex)

    for j in range(random_n_qubits):
        ops = [id_mat] * random_n_qubits
        ops[j] = sigma_x
        term = reduce(np.kron, ops)
        H += term

    # Compute unitary
    U = expm(-1j * 0.5 * random_rotation_angle * H)

    return U
