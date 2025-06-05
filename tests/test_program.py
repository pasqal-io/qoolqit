from __future__ import annotations

from typing import Callable

import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit.devices import ALL_DEVICES
from qoolqit.drive import Drive
from qoolqit.program import QuantumProgram
from qoolqit.register import Register


@pytest.mark.repeat(2)
@pytest.mark.parametrize("device_class", ALL_DEVICES)
def test_program_init_and_compilation(
    device_class: Callable,
    random_register: Callable[[], Register],
    random_drive: Callable[[], Drive],
) -> None:

    register = random_register()
    drive = random_drive()
    program = QuantumProgram(register, drive)
    assert not program.is_compiled

    with pytest.raises(ValueError):
        program.compiled_sequence

    device = device_class()
    program.compile_to(device)
    assert program.is_compiled
    assert isinstance(program.compiled_sequence, PulserSequence)
