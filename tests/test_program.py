from __future__ import annotations

import json
from typing import Callable

import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit import AnalogDevice, Device, DigitalAnalogDevice, MockDevice
from qoolqit import __version__ as qoolqit_version
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
from qoolqit.execution import CompilerProfile
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import Ramp

QOOLQIT_DEFAULT_DEVICES = [AnalogDevice, DigitalAnalogDevice, MockDevice]


@pytest.mark.flaky(max_runs=2)
@pytest.mark.parametrize("device_class", QOOLQIT_DEFAULT_DEVICES)
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


@pytest.mark.flaky(max_runs=2)
@pytest.mark.parametrize(
    "device_class, profile",
    [
        (AnalogDevice, CompilerProfile.DEFAULT),
        (AnalogDevice, CompilerProfile.MAX_AMPLITUDE),
        (AnalogDevice, CompilerProfile.MAX_DURATION),
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

    # FIXME: Reactivate the min_distance profile once we implement safe-mode compilation
    # Currently trying to set the atoms at the min distance will very often cause the
    # amplitude to go over the limit allowed for the channel, which will fail the compilation.
    if profile != CompilerProfile.MIN_DISTANCE:
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

    if profile != CompilerProfile.MIN_DISTANCE:
        program = dmm_program()
        device = device_class()
        if device._device.dmm_channels:
            program.compile_to(device, profile=profile)
            assert program.is_compiled
            assert isinstance(program.compiled_sequence, PulserSequence)
        else:
            with pytest.raises(CompilationError):
                program.compile_to(device, profile=profile)


def test_compiled_sequence_metadata(random_program: Callable[[], QuantumProgram]) -> None:
    program = random_program()
    program.compile_to(MockDevice())
    compiled_seq_repr = json.loads(program.compiled_sequence.to_abstract_repr())

    compiled_seq_metadata = compiled_seq_repr["metadata"]
    expected_metadata = {"package_versions": {"qoolqit": qoolqit_version}, "extra": {}}
    assert compiled_seq_metadata == expected_metadata


def test_validate_program() -> None:
    pass


@pytest.mark.parametrize(
    "device, profile",
    [
        (MockDevice(), CompilerProfile.MAX_AMPLITUDE),
        (MockDevice(), CompilerProfile.MAX_DURATION),
        (MockDevice(), CompilerProfile.MIN_DISTANCE),
        (DigitalAnalogDevice(), CompilerProfile.MAX_DURATION),
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
