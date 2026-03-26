from __future__ import annotations

from typing import Callable

import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit import AnalogDevice, DigitalAnalogDevice, MockDevice
from qoolqit.devices import Device
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
from qoolqit.program import QuantumProgram
from qoolqit.register import Register
from qoolqit.waveforms import Constant


def test_program_init() -> None:
    register = Register(qubits={"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
    drive = Drive(amplitude=Constant(1.0, 1.0), detuning=Constant(1.005, 1.0))
    program = QuantumProgram(register=register, drive=drive)
    assert program.register == register
    assert program.drive == drive
    assert not program.is_compiled

    with pytest.raises(ValueError, match="Program has not been compiled"):
        program.compiled_sequence


@pytest.mark.parametrize(
    "device",
    [DigitalAnalogDevice(), MockDevice()],
)
def test_compiler_dmm(
    device: Device,
    dmm_program: Callable[[], QuantumProgram],
) -> None:
    program = dmm_program()
    if device._device.dmm_channels:
        program.compile_to(device)
        assert program.is_compiled
        assert isinstance(program.compiled_sequence, PulserSequence)
    else:
        with pytest.raises(CompilationError):
            program.compile_to(device)


def test_compiled_sequence_with_small_delays() -> None:
    """Test that the added delay is not compiled into the pulser sequence if smaller that 1 ns."""
    register = Register(qubits={"q0": (0.0, 0.0), "q1": (1.0, 0.0)})

    drive = Drive(amplitude=Constant(1.0, 1.0), detuning=Constant(1.0, 1.0))
    drive_small_delay = Drive(amplitude=Constant(1.0, 1.0), detuning=Constant(1.005, 1.0))

    program = QuantumProgram(register=register, drive=drive)
    program.compile_to(device=AnalogDevice())
    program_small_delay = QuantumProgram(register=register, drive=drive_small_delay)
    program_small_delay.compile_to(device=AnalogDevice())

    # check that the delay is not added to the pulser sequence if small
    pulser_duration = program.compiled_sequence.get_duration()
    pulser_duration_small_delay = program_small_delay.compiled_sequence.get_duration()
    assert pulser_duration == pulser_duration_small_delay


def test_compile_to_max_duration() -> None:
    """Test that the compiled sequence's duration is set to the maximum allowed by the device."""
    register = Register(qubits={"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
    drive = Drive(amplitude=Constant(2.0, 1.0))
    program = QuantumProgram(register=register, drive=drive)
    device = AnalogDevice()

    expected_max_duration = device._max_duration

    program.compile_to(device=AnalogDevice(), max_duration=True)
    assert program.is_compiled
    assert program.compiled_sequence.get_duration() == expected_max_duration
