from __future__ import annotations

from typing import Callable

import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit import AnalogDevice, Device, DigitalAnalogDevice, MockDevice
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
from qoolqit.execution import CompilerProfile
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import Constant, Ramp


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
    "device_class, profile",
    [
        (AnalogDevice, CompilerProfile.DEFAULT),
        (AnalogDevice, CompilerProfile.MAX_AMPLITUDE),
        (AnalogDevice, CompilerProfile.MIN_DISTANCE),
        (DigitalAnalogDevice, CompilerProfile.DEFAULT),
        (DigitalAnalogDevice, CompilerProfile.MAX_AMPLITUDE),
        (DigitalAnalogDevice, CompilerProfile.MIN_DISTANCE),
        (MockDevice, CompilerProfile.DEFAULT),
    ],
)
def test_compiler_profiles(
    device_class: Callable, profile: CompilerProfile, random_program: Callable[[], QuantumProgram]
) -> None:
    program = random_program()
    device = device_class()
    program.compile_to(device, profile=profile)
    assert program.is_compiled
    assert isinstance(program.compiled_sequence, PulserSequence)


@pytest.mark.parametrize(
    "device_class, profile",
    [
        (DigitalAnalogDevice, CompilerProfile.DEFAULT),
        (DigitalAnalogDevice, CompilerProfile.MAX_AMPLITUDE),
        (DigitalAnalogDevice, CompilerProfile.MIN_DISTANCE),
        (MockDevice, CompilerProfile.DEFAULT),
    ],
)
def test_compiler_profiles_dmm(
    device_class: Callable,
    profile: CompilerProfile,
    dmm_program: Callable[[], QuantumProgram],
) -> None:
    program = dmm_program()
    device = device_class()
    if device._device.dmm_channels:
        program.compile_to(device, profile=profile)
        assert program.is_compiled
        assert isinstance(program.compiled_sequence, PulserSequence)
    else:
        with pytest.raises(CompilationError):
            program.compile_to(device, profile=profile)


def test_compiled_sequence_with_delays() -> None:
    """Test that the added delay is not compiled into the pulser sequence if smaller that 1 ns."""
    register = Register(qubits={"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
    drive = Drive(amplitude=Constant(1.0, 1.0), detuning=Constant(1.005, 1.0))
    program = QuantumProgram(register=register, drive=drive)
    program.compile_to(device=AnalogDevice())

    pulser_duration = program.compiled_sequence.get_duration()
    assert pulser_duration == 80


def test_validate_program_catch_compilation_error_max_amp() -> None:
    register = Register({"q0": (0.0, 0.0), "q1": (1.0, 1.0)})
    drive = Drive(amplitude=Constant(50, value=1.1))
    program = QuantumProgram(register, drive)
    with pytest.raises(
        CompilationError,
        match=(
            "The drive's maximum amplitude 1.1 goes over "
            "the maximum value allowed for the chosen device"
        ),
    ):
        program.compile_to(device=AnalogDevice())


def test_validate_program_catch_compilation_error_max_det() -> None:
    register = Register({"q0": (0.0, 0.0), "q1": (1.0, 1.0)})
    drive = Drive(amplitude=Constant(50, value=0.9), detuning=Constant(50, value=100))
    program = QuantumProgram(register, drive)
    with pytest.raises(
        CompilationError,
        match=(
            "The drive's maximum absolute detuning 100.0 goes over "
            "the maximum value allowed for the chosen device"
        ),
    ):
        program.compile_to(device=AnalogDevice())


def test_validate_program_catch_compilation_error_max_duration() -> None:
    register = Register({"q0": (0.0, 0.0), "q1": (1.0, 1.0)})
    drive = Drive(amplitude=Constant(123.0, value=0.9))
    program = QuantumProgram(register, drive)
    with pytest.raises(
        CompilationError,
        match=(
            "The drive's duration 123.0 goes over the maximum value allowed for the chosen device"
        ),
    ):
        program.compile_to(device=AnalogDevice())


def test_validate_program_catch_compilation_error_min_dist() -> None:
    register = Register({"q0": (-0.1, 0.0), "q1": (0.1, 0.0)})
    drive = Drive(amplitude=Constant(10.0, 0.5))
    program = QuantumProgram(register, drive)
    with pytest.raises(
        CompilationError,
        match=(
            "The register minimum distance between two qubits 0.2 goes below "
            "the minimum allowed for the chosen device"
        ),
    ):
        program.compile_to(device=AnalogDevice())


def test_validate_program_catch_compilation_error_max_dist() -> None:
    register = Register({"q0": (0.0, 0.0), "q1": (10.0, 0.0)})
    drive = Drive(amplitude=Constant(13.0, 0.2))
    program = QuantumProgram(register, drive)
    with pytest.raises(
        CompilationError,
        match=(
            "The register maximum radial distance 10.0 goes over "
            "the maximum allowed for the chosen device"
        ),
    ):
        program.compile_to(device=AnalogDevice())


@pytest.mark.parametrize(
    "device, profile",
    [
        (MockDevice(), CompilerProfile.MAX_AMPLITUDE),
        (MockDevice(), CompilerProfile.MIN_DISTANCE),
    ],
)
def test_validate_program_unsupported_profile(device: Device, profile: CompilerProfile) -> None:
    register = Register({f"q{i}": (i, i) for i in range(3)})
    drive = Drive(amplitude=Ramp(50, initial_value=0.6, final_value=0.8))
    program = QuantumProgram(register, drive)
    with pytest.raises(
        CompilationError, match="the target min/max value is not specified in the chosen device"
    ):
        program.compile_to(device=device, profile=profile)
