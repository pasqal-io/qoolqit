from __future__ import annotations

from typing import Callable

import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit import AnalogDevice, DigitalAnalogDevice, MockDevice
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
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
