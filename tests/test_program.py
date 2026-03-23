from __future__ import annotations

from typing import Callable

import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit import AnalogDevice, DigitalAnalogDevice, MockDevice
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
from qoolqit.execution.compilation_functions import CompilerProfile
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import Constant


@pytest.mark.parametrize("device_class", [AnalogDevice, DigitalAnalogDevice, MockDevice])
def test_program_init_and_compilation(
    device_class: Callable,
    random_linear_register: Callable[[], Register],
    random_drive: Callable[[], Drive],
) -> None:

    register = random_linear_register()
    drive = random_drive()
    program = QuantumProgram(register, drive)
    assert not program.is_compiled

    with pytest.raises(ValueError):
        program.compiled_sequence

    device = device_class()
    program.compile_to(device)
    assert program.is_compiled
    assert isinstance(program.compiled_sequence, PulserSequence)


@pytest.mark.parametrize(
    "device_class",
    [DigitalAnalogDevice, MockDevice],
)
def test_compiler_dmm(
    device_class: Callable,
    dmm_program: Callable[[], QuantumProgram],
) -> None:
    program = dmm_program()
    device = device_class()
    if device._device.dmm_channels:
        program.compile_to(device)
        assert program.is_compiled
        assert isinstance(program.compiled_sequence, PulserSequence)
    else:
        with pytest.raises(CompilationError):
            program.compile_to(device)


def test_compiled_sequence_with_delays() -> None:
    """Test that the added delay is not compiled into the pulser sequence if smaller that 1 ns."""
    register = Register(qubits={"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
    drive = Drive(amplitude=Constant(1.0, 1.0), detuning=Constant(1.005, 1.0))
    program = QuantumProgram(register=register, drive=drive)
    program.compile_to(device=AnalogDevice())

    pulser_duration = program.compiled_sequence.get_duration()
    assert pulser_duration == 80


def test_catch_compilation_error_max_det() -> None:
    register = Register({"q0": (0.0, 0.0), "q1": (1.0, 1.0)})
    drive = Drive(amplitude=Constant(50, value=0.9), detuning=Constant(50, value=100))
    program = QuantumProgram(register, drive)

    # expected wrong max detuning after compilation
    expected_max_abs_detuning = 100.0 / 0.9

    with pytest.raises(
        CompilationError,
        match=(
            f"The drive's maximum absolute detuning {expected_max_abs_detuning:.3f} goes over "
            "the maximum value allowed for the chosen device"
        ),
    ):
        program.compile_to(device=AnalogDevice(), profile=CompilerProfile.DEFAULT)


def test_catch_compilation_error_max_duration() -> None:
    register = Register({"q0": (0.0, 0.0), "q1": (1.0, 1.0)})
    drive = Drive(amplitude=Constant(123.0, value=0.9))
    program = QuantumProgram(register, drive)

    # expected wrong duration after compilation
    expected_duration = 123.0 * 0.9

    with pytest.raises(
        CompilationError,
        match=(
            f"The drive's duration {expected_duration:.3f} "
            "goes over the maximum value allowed for the chosen device"
        ),
    ):
        program.compile_to(device=AnalogDevice())


def test_catch_compilation_error_max_duration_from_min_dist() -> None:
    # this test can be removed once the minimum distance is constrained to
    # be only larger than 1.0
    min_distance = 0.2
    register = Register({"q0": (-min_distance / 2, 0.0), "q1": (min_distance / 2, 0.0)})
    drive = Drive(amplitude=Constant(10.0, 0.5))
    program = QuantumProgram(register, drive)
    device = AnalogDevice()

    # expected wrong duration after compilation to min distance
    device_min_distance = device.specs["min_distance"]
    assert isinstance(device_min_distance, float)
    expected_wrong_duration = 10.0 * (device_min_distance / min_distance) ** 6

    with pytest.raises(
        CompilationError,
        match=(
            f"The drive's duration {expected_wrong_duration:.3f} goes over "
            "the maximum value allowed for the chosen device"
        ),
    ):
        program.compile_to(device=device)


def test_catch_compilation_error_max_dist() -> None:
    register = Register({"q0": (0.0, 0.0), "q1": (9.0, 0.0)})
    drive = Drive(amplitude=Constant(13.0, 0.2))
    program = QuantumProgram(register, drive)

    # expected wrong max distance after compilation
    # in adimensional units distance rescaling factor = (max_amp/max_amp_drive)^(-1/6)
    expected_max_radial_distance = 9.0 * (1 / 0.2) ** (-1 / 6)

    with pytest.raises(
        CompilationError,
        match=(
            f"The register maximum radial distance {expected_max_radial_distance:.3f} goes over "
            "the maximum allowed for the chosen device"
        ),
    ):
        program.compile_to(device=AnalogDevice())
