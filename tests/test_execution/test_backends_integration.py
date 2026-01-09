from __future__ import annotations

from typing import Callable

import numpy as np
import pytest
from pulser.backend import Backend, Occupation

from qoolqit import AnalogDevice, Constant, Drive, MockDevice, QuantumProgram, Register
from qoolqit.devices import Device
from qoolqit.execution import BackendType, EmulationConfig, LocalEmulator

backends_list = (BackendType.QutipBackendV2, BackendType.SVBackend, BackendType.MPSBackend)


@pytest.mark.parametrize("rotation_angle", [0.3 * np.pi])
@pytest.mark.parametrize("backend_type", backends_list)
def test_theoretical_state_vector(backend_type: Backend, rotation_angle: float) -> None:

    # Theoretical excited population after X rotation
    # exp(-iθσₓ/2)|g❭ = [cos(θ/2)I - i*sin(θ/2)σₓ]|g❭
    expected_r_pop = np.sin(rotation_angle / 2) ** 2
    n_qubits = 4

    # Create and run a quantum program with different backends
    duration = 4 * np.pi
    drive = Drive(amplitude=Constant(duration, rotation_angle / duration), phase=0)
    # atoms far away, no interaction
    register = Register.from_coordinates([(x * 100.0, 0.0) for x in np.arange(n_qubits)])
    program = QuantumProgram(register, drive)
    program.compile_to(MockDevice())
    emulation_config = EmulationConfig(observables=(Occupation(),))
    emulator = LocalEmulator(backend_type=backend_type, emulation_config=emulation_config)
    res = emulator.run(program)[0]

    final_r_pop = res.occupation

    assert np.allclose(final_r_pop, expected_r_pop, rtol=1e-3)


@pytest.mark.parametrize(
    "backend_type, device",
    [
        (BackendType.SVBackend, MockDevice()),
        (BackendType.SVBackend, AnalogDevice()),
        (BackendType.MPSBackend, MockDevice()),
        (BackendType.MPSBackend, AnalogDevice()),
    ],
)
def test_results(random_program: Callable, backend_type: Backend, device: Device) -> None:
    # Just run once and test multiple things for efficiency

    # Create a quantum program
    program = random_program()
    program.compile_to(device)

    # Run with QUTIP backend as reference
    runs = 1001  # how many bitstrings to sample
    steps = 20
    evaluation_times = np.linspace(0, 1, steps).tolist()
    config = EmulationConfig(observables=(Occupation(evaluation_times=evaluation_times),))
    qutip_emulator = LocalEmulator(emulation_config=config, runs=runs)
    qutip_res = qutip_emulator.run(program)[0]
    qutip_occupation = qutip_res.occupation
    # assert final time bitstrings dict is present, with `runs` entries
    qutip_bitstrings = qutip_res.final_bitstrings
    assert sum(qutip_bitstrings.values()) == runs

    # Run with other backend
    other_emulator = LocalEmulator(backend_type=backend_type, emulation_config=config, runs=runs)
    other_res = other_emulator.run(program)[0]
    other_occupation = other_res.occupation
    # assert final time bitstrings dict is present, with `runs` entries
    other_bitstrings = other_res.final_bitstrings
    assert sum(other_bitstrings.values()) == runs

    # Test result observables tags
    expected_tags = {"occupation", "bitstrings"}
    qutip_obs_tags = qutip_res.get_result_tags()
    assert expected_tags <= set(qutip_obs_tags)
    other_obs_tags = other_res.get_result_tags()
    assert expected_tags <= set(other_obs_tags)

    # Test evaluation times
    qutip_eval_times = qutip_res.get_result_times("occupation")
    assert np.allclose(qutip_eval_times, evaluation_times, atol=1e-12)
    # Emulators below:
    # - skip the t=0 evaluation time
    # - alter user input evaluation times
    # - will fail for even steps
    # TODO: review this test when https://github.com/pasqal-io/emulators/issues/169 is solved
    other_eval_times = other_res.get_result_times("occupation")
    if backend_type in (BackendType.SVBackend, BackendType.MPSBackend):
        assert np.allclose(other_eval_times, evaluation_times[1:], atol=0.05)

    # value comparison of result is not fair because of different evaluation times
    # TODO: review this test when https://github.com/pasqal-io/emulators/issues/169 is solved
    assert np.allclose(qutip_occupation[1:], other_occupation, atol=0.2)
