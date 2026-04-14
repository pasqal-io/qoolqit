from __future__ import annotations

from typing import Callable

import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit import AnalogDevice, DataGraph, DigitalAnalogDevice, MockDevice
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


@pytest.mark.parametrize("ratio", [0.33, 0.5, 1.0])
def test_compile_to_max_duration_ratio(ratio: float) -> None:
    """Test `device_max_duration_ratio` compilation flag.

    Check that that the compiled sequence's duration is set to the ratio
    of the maximum duration allowed by the device.
    """
    register = Register(qubits={"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
    drive = Drive(amplitude=Constant(2.0, 1.0))
    program = QuantumProgram(register=register, drive=drive)
    device = AnalogDevice()
    assert device._max_duration == 6000

    expected_max_duration = round(ratio * device._max_duration)

    program.compile_to(device=device, device_max_duration_ratio=ratio)
    assert program.is_compiled
    assert program.compiled_sequence.get_duration() == expected_max_duration


@pytest.mark.parametrize("duration", [2.0, 33.33, 1000.0])
def test_compile_to_max_duration(duration: float) -> None:
    """Test that the compiled sequence's duration is set to the maximum allowed by the device."""
    reg = Register.from_graph(DataGraph.line(2))
    amp = Constant(duration=duration, value=1.0)
    drive = Drive(amplitude=amp)
    program = QuantumProgram(reg, drive)
    program.compile_to(AnalogDevice(), device_max_duration_ratio=1.0)

    assert program.is_compiled
    assert program.compiled_sequence.get_duration() == 6000


def test_max_duration_ratio_error() -> None:
    """Test that a ValueError is raised when the device_max_duration_ratio is not in (0,1]."""
    register = Register(qubits={"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
    drive = Drive(amplitude=Constant(2.0, 1.0))
    program = QuantumProgram(register=register, drive=drive)

    with pytest.raises(ValueError, match="`device_max_duration_ratio` must be between 0 and 1,"):
        program.compile_to(device=AnalogDevice(), device_max_duration_ratio=-0.1)

    with pytest.raises(ValueError, match="Cannot set `device_max_duration_ratio`"):
        program.compile_to(device=MockDevice(), device_max_duration_ratio=0.5)
