from __future__ import annotations

from typing import Callable

import numpy as np
import pytest
from pulser.backend import Backend, Occupation

from qoolqit import AnalogDevice, Constant, Drive, MockDevice, QuantumProgram, Register
from qoolqit.devices import Device
from qoolqit.execution import EmulationConfig, LocalEmulator, MPSBackend, QutipBackendV2, SVBackend

backends_list = (QutipBackendV2, SVBackend, MPSBackend)


@pytest.mark.parametrize("backend_type", backends_list)
def test_theoretical_state_vector(backend_type: Backend, random_rotation_angle: float) -> None:

    # Theoretical excited population after X rotation
    # exp(-iθσₓ/2)|g❭ = [cos(θ/2)I - i*sin(θ/2)σₓ]|g❭
    expected_r_pop = np.sin(random_rotation_angle / 2) ** 2
    n_qubits = 4

    # Create and run a quantum program with different backends
    duration = 4 * np.pi
    random_rotation_angle = random_rotation_angle / duration
    drive = Drive(amplitude=Constant(duration, random_rotation_angle), phase=0)
    # atoms far away, no interaction
    register = Register.from_coordinates([(x * 100.0, 0.0) for x in np.arange(n_qubits)])
    program = QuantumProgram(register, drive)
    program.compile_to(MockDevice())
    emulation_config = EmulationConfig(observables=(Occupation(),))
    emulator = LocalEmulator(backend_type=backend_type, emulation_config=emulation_config)
    res = emulator.run(program)

    final_r_pop = res[0].occupation

    assert np.allclose(final_r_pop, expected_r_pop, rtol=1e-3)


@pytest.mark.parametrize(
    "backend_type, device",
    [
        (SVBackend, MockDevice()),
        (SVBackend, AnalogDevice()),
        (MPSBackend, MockDevice()),
        (MPSBackend, AnalogDevice()),
    ],
)
def test_results(random_program: Callable, backend_type: Backend, device: Device) -> None:
    # Create a quantum program
    program = random_program()
    program.compile_to(device)

    # Run with QUTIP backend as reference
    config = EmulationConfig(observables=(Occupation(),))
    qutip_emulator = LocalEmulator(emulation_config=config)
    qutip_res = qutip_emulator.run(program)
    qutip_occupation = qutip_res[0].occupation

    # Run with other backend
    other_emulator = LocalEmulator(backend_type=backend_type, emulation_config=config)
    other_res = other_emulator.run(program)
    other_occupation = other_res[0].occupation

    assert np.allclose(qutip_occupation, other_occupation, rtol=0.1)


@pytest.mark.parametrize(
    "backend_type, device",
    [
        (SVBackend, MockDevice()),
        (SVBackend, AnalogDevice()),
        (MPSBackend, MockDevice()),
        (MPSBackend, AnalogDevice()),
    ],
)
def test_bitstrings(random_program: Callable, backend_type: Backend, device: Device) -> None:
    # Create a quantum program
    program = random_program()
    program.compile_to(device)
    runs = 1000

    # Run with QUTIP backend as reference
    qutip_emulator = LocalEmulator(runs=runs)
    qutip_res = qutip_emulator.run(program)
    qutip_bitstrings = qutip_res[0].final_bitstrings

    # Run with other backend
    other_emulator = LocalEmulator(backend_type=backend_type, runs=runs)
    other_res = other_emulator.run(program)
    other_bitstrings = other_res[0].final_bitstrings

    # Get union of all keys
    all_keys = set(qutip_bitstrings.keys()).union(other_bitstrings.keys())

    # Normalize both counters
    p1 = {key: qutip_bitstrings.get(key, 0) / runs for key in all_keys}
    p2 = {key: other_bitstrings.get(key, 0) / runs for key in all_keys}

    # Compare with tolerance
    similar = True
    for key in all_keys:
        diff = abs(p1[key] - p2[key])
        if diff > 0.05:
            similar = False

    assert similar


@pytest.mark.parametrize("backend_type", backends_list)
@pytest.mark.parametrize("steps", [20, 30, 40])
def test_evaluation_times(random_program: Callable, backend_type: Backend, steps: int) -> None:
    # this test fail for even number of steps because emulators
    # do not respect the evaluation times passed by the user
    # TODO: asses again when the issue is solved

    # Create a quantum program
    program = random_program()
    program.compile_to(MockDevice())

    # configure evaluation times and run
    evaluation_times = np.linspace(0.1, 1, steps).tolist()
    config = EmulationConfig(observables=(Occupation(evaluation_times=evaluation_times),))
    emulator = LocalEmulator(backend_type=backend_type, emulation_config=config)

    res = emulator.run(program)
    obs_res = res[0].occupation

    assert len(obs_res) == len(evaluation_times)
