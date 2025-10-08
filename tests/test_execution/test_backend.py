from __future__ import annotations

from typing import Callable

import numpy as np
import pytest
from metrics import ATOL_BITSTRINGS, ATOL_STATE_VEC

from qoolqit import AnalogDevice, Constant, Drive, MockDevice, QuantumProgram, Register
from qoolqit.devices import Device
from qoolqit.execution import BackendName, ResultType


@pytest.mark.flaky(max_runs=5)
@pytest.mark.parametrize("backend_name", BackendName.list())
def test_theoretical_state_vector(
    backend_name: BackendName, random_x_rotation: np.ndarray, random_rotation_angle: float
) -> None:
    if backend_name == BackendName.EMUMPS:
        pytest.skip("EmuMPS is only available under Unix")
        return

    # Theoretical final state after X rotation
    theor_state = random_x_rotation[:, 0]
    n_qubits = int(np.log2(len(theor_state)))

    # Create and run a quantum program with different backends
    random_rotation_angle = 0.25 * random_rotation_angle / np.pi
    drive = Drive(amplitude=Constant(4 * np.pi, random_rotation_angle), phase=0)
    register = Register.from_coordinates([(x * 100.0, 0.0) for x in np.arange(n_qubits)])
    program = QuantumProgram(register, drive)
    program.compile_to(MockDevice())
    res = program.run(backend_name=backend_name, result_type=ResultType.STATEVECTOR)[-1]

    assert np.isclose(theor_state, res, atol=ATOL_STATE_VEC).all()


@pytest.mark.parametrize(
    "backend_name, device",
    [
        pytest.param(BackendName.EMUMPS, MockDevice(), marks=pytest.mark.flaky(max_runs=5)),
        pytest.param(
            BackendName.EMUMPS,
            AnalogDevice(),
        ),
    ],
)
def test_state_vector(random_program: Callable, backend_name: BackendName, device: Device) -> None:
    # Create a quantum program
    program = random_program()
    program.compile_to(device)

    # Run with QUTIP backend as reference
    qutip_res = program.run(backend_name=BackendName.QUTIP, result_type=ResultType.STATEVECTOR)[-1]

    # Run with other backend
    bknd_res = program.run(backend_name=backend_name, result_type=ResultType.STATEVECTOR)[-1]

    assert np.isclose(qutip_res, bknd_res, atol=ATOL_STATE_VEC).all()


@pytest.mark.flaky(max_runs=5)
@pytest.mark.parametrize(
    "backend_name, device",
    [
        pytest.param(
            BackendName.EMUMPS,
            MockDevice(),
            marks=[
                pytest.mark.flaky(max_runs=5),
            ],
        ),
        pytest.param(
            BackendName.EMUMPS,
            AnalogDevice(),
        ),
    ],
)
def test_bitstrings(random_program: Callable, backend_name: BackendName, device: Device) -> None:
    # Create a quantum program
    program = random_program()
    program.compile_to(device)
    runs = 1000

    # Run with QUTIP backend as reference
    qutip_res = program.run(
        backend_name=BackendName.QUTIP, result_type=ResultType.BITSTRINGS, runs=runs
    )[-1]

    # Run with other backend
    bknd_res = program.run(backend_name=backend_name, result_type=ResultType.BITSTRINGS, runs=runs)[
        -1
    ]

    # Get union of all keys
    all_keys = set(qutip_res.keys()).union(bknd_res.keys())

    # Normalize both counters
    p1 = {key: qutip_res.get(key, 0) / runs for key in all_keys}
    p2 = {key: bknd_res.get(key, 0) / runs for key in all_keys}

    # Compare with tolerance
    similar = True
    for key in all_keys:
        diff = abs(p1[key] - p2[key])
        if diff > ATOL_BITSTRINGS:
            similar = False

    assert similar


@pytest.mark.flaky(max_runs=5)
@pytest.mark.parametrize(
    "backend_name",
    [
        pytest.param(BackendName.QUTIP),
        pytest.param(BackendName.EMUMPS),
    ],
)
@pytest.mark.parametrize("result_type", [ResultType.STATEVECTOR, ResultType.BITSTRINGS])
def test_evaluation_times(
    random_program: Callable, backend_name: BackendName, result_type: ResultType
) -> None:
    # Create a quantum program
    program = random_program()
    program.compile_to(MockDevice())

    # Run with other backend
    evaluation_times = np.linspace(0, 1, np.random.randint(50, 200)).tolist()
    bknd_res = program.run(
        backend_name=backend_name, result_type=result_type, evaluation_times=evaluation_times
    )

    assert len(bknd_res) == len(evaluation_times)
