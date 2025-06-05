from __future__ import annotations

from typing import Callable

import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit.devices import ALL_DEVICES
from qoolqit.drive import Drive
from qoolqit.execution import CompilerProfile
from qoolqit.program import QuantumProgram
from qoolqit.register import Register


@pytest.mark.repeat(2)
@pytest.mark.parametrize("device_class", ALL_DEVICES)
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


@pytest.mark.repeat(3)
@pytest.mark.parametrize("device_class", ALL_DEVICES)
@pytest.mark.parametrize("profile", CompilerProfile.list())
def test_compiler_profiles(
    device_class: Callable, profile: CompilerProfile, random_program: Callable[[], QuantumProgram]
) -> None:

    program = random_program()
    device = device_class()
    program.compile_to(device, profile=profile)
    assert program.is_compiled
    assert isinstance(program.compiled_sequence, PulserSequence)
