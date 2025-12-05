from __future__ import annotations

from typing import Callable

import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit import AnalogDevice, DigitalAnalogDevice, MockDevice
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
from qoolqit.execution import CompilerProfile
from qoolqit.program import QuantumProgram
from qoolqit.register import Register

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
@pytest.mark.parametrize("device_class", QOOLQIT_DEFAULT_DEVICES)
@pytest.mark.parametrize("profile", CompilerProfile.list())
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


@pytest.mark.parametrize("device_class", QOOLQIT_DEFAULT_DEVICES)
@pytest.mark.parametrize("profile", CompilerProfile.list())
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
