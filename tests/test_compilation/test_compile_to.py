"""Test compilation independently on the compilation profiles."""

from __future__ import annotations

import json
from typing import Literal
from unittest.mock import MagicMock

import numpy as np
import pytest
from pulser import AnalogDevice as PulserAnalogDevice
from pulser.sampler import sample

from qoolqit import AnalogDevice, Drive, MockDevice, QuantumProgram, Register
from qoolqit.devices import Device
from qoolqit.drive import DetuningMapModulator
from qoolqit.exceptions import CompilationError
from qoolqit.execution.compilation_functions import CompilerProfile
from qoolqit.waveforms import ConstantWaveform


@pytest.mark.parametrize(
    "profile",
    [
        CompilerProfile.MAX_ENERGY,
        CompilerProfile.DEFAULT,
        "max_energy",
        "default",
    ],
)
def test_compilation_single_qubit(
    profile: Literal["max_energy", "default"] | CompilerProfile,
) -> None:
    """Test compilation of a single-qubit program."""
    register = Register(qubits={"q0": (0.0, 0.0)})
    drive = Drive(amplitude=ConstantWaveform(2.0, 0.2))
    program = QuantumProgram(register=register, drive=drive)

    program.compile_to(device=AnalogDevice(), profile=profile)
    assert program.is_compiled


def test_compiler_profile_deprecated_working_point_alias() -> None:
    """Test that WORKING_POINT is aliases of DEFAULT."""
    assert CompilerProfile.WORKING_POINT is CompilerProfile.DEFAULT
    assert CompilerProfile("default") is CompilerProfile.DEFAULT


def test_compile_to_invalid_profile_string() -> None:
    """Test compilation with an invalid profile string alias."""
    register = Register(qubits={"q0": (0.0, 0.0)})
    drive = Drive(amplitude=ConstantWaveform(2.0, 0.2))
    program = QuantumProgram(register=register, drive=drive)
    with pytest.raises(ValueError, match="'bogus' is not a valid CompilerProfile"):
        program.compile_to(device=AnalogDevice(), profile="bogus")  # type: ignore [arg-type]


def test_dmm_not_supported() -> None:
    """Test compilation of a program with a DMM but the device does not support it."""
    mock_register = MagicMock(spec=Register)
    mock_dmm = MagicMock(spec=DetuningMapModulator, weights={})
    mock_drive = MagicMock(spec=Drive, dmm=mock_dmm)
    program = QuantumProgram(register=mock_register, drive=mock_drive)
    with pytest.raises(CompilationError, match="The device does not support DMM"):
        # AnalogDevice does not support DMM
        program.compile_to(device=AnalogDevice())


@pytest.mark.parametrize("profile", [CompilerProfile.MAX_ENERGY, CompilerProfile.DEFAULT])
def test_compilation_with_dmm(profile: CompilerProfile) -> None:
    """Test compilation of a program with a DMM."""
    register = Register(qubits={"q0": (0.0, 0.7), "q1": (-0.5, -0.5), "q2": (0.5, -0.5)})

    amplitude = ConstantWaveform(5.0, 0.5)
    detuning = ConstantWaveform(5.0, -1.23)
    dmm = DetuningMapModulator(
        waveform=ConstantWaveform(5.0, -1.23), weights={"q0": 0.1, "q1": 0.2, "q2": 0.9}
    )
    drive = Drive(amplitude=amplitude, detuning=detuning, dmm=dmm)
    program = QuantumProgram(register=register, drive=drive)

    # Test compilation on the default profile
    program.compile_to(device=MockDevice(), profile=profile)
    assert program.is_compiled

    # check pulser sequence contains expected DMM values by sampling the sequence
    pulser_sequence = program.compiled_sequence
    assert set(pulser_sequence.declared_channels.keys()) == {"rydberg", "dmm_0"}

    pulser_sequence_sample = sample(pulser_sequence)
    rydberg_sample = pulser_sequence_sample.channel_samples["rydberg"]
    dmm_sample = pulser_sequence_sample.channel_samples["dmm_0"]

    # check detunings are scaled correctly by compilation
    np.testing.assert_allclose(rydberg_sample.det, dmm_sample.det, atol=1e-8)

    dmm_weights = dmm_sample.detuning_map.weights
    assert dmm_weights == (0.1, 0.2, 0.9)


def test_compile_to_wrong_device_type() -> None:
    """Test compilation to a device with a different type."""
    register = Register(qubits={"q0": (0.0, 0.0)})
    drive = Drive(amplitude=ConstantWaveform(2.0, 0.2))
    program = QuantumProgram(register=register, drive=drive)
    with pytest.raises(TypeError, match="`device` must be of type `qoolqit.devices.Device`."):
        program.compile_to(device="I'm not a device")  # type: ignore [arg-type]
    with pytest.raises(TypeError, match="`device` must be of type `qoolqit.devices.Device`."):
        program.compile_to(device=PulserAnalogDevice)  # type: ignore [arg-type]


def test_compilation_composite_drive_produces_multiple_pulses_in_order() -> None:
    # a drive composed of segments with different phases compiles to one pulse per segment
    register = Register(qubits={"q0": (0.0, 0.0)})
    amp = ConstantWaveform(2.0, 0.2)
    det = ConstantWaveform(2.0, 0.0)

    drive_1 = Drive(amplitude=amp, detuning=det, phase=np.pi)
    drive_2 = Drive(amplitude=amp, detuning=det, phase=0.0)
    drive = drive_1 >> drive_2

    program = QuantumProgram(register=register, drive=drive)
    program.compile_to(device=MockDevice())

    compiled_sequence = program.compiled_sequence
    compiled_sequence_repr = json.loads(compiled_sequence.to_abstract_repr())
    pulses_repr = [
        pulse for pulse in compiled_sequence_repr["operations"] if pulse["op"] == "pulse"
    ]

    phases = [pulse["phase"] for pulse in pulses_repr]
    np.testing.assert_allclose(phases, [np.pi, 0.0])


def test_compilation_same_phase_composition_has_no_extra_delay() -> None:
    # composing two same-phase drives adds no delay, even on a device with phase_jump_time > 0
    register = Register(qubits={"q0": (0.0, 0.0)})
    amp = ConstantWaveform(2.0, 0.2)
    det = ConstantWaveform(2.0, 0.0)
    drive = Drive(amplitude=amp, detuning=det, phase=np.pi)
    composite = drive >> drive

    single_program = QuantumProgram(register=register, drive=drive)
    single_program.compile_to(device=AnalogDevice())

    composite_program = QuantumProgram(register=register, drive=composite)
    composite_program.compile_to(device=AnalogDevice())

    assert composite_program.compiled_sequence.get_duration() == (
        2 * single_program.compiled_sequence.get_duration()
    )


def test_compilation_same_phase_composition_fits_device_max_duration() -> None:
    # same-phase segments compile to a single pulse, so the clock period rounding
    # is applied once and the sequence exactly matches the device max duration
    register = Register(qubits={"q0": (0.0, 0.0)})
    drive_1 = Drive(amplitude=ConstantWaveform(1.3, 0.2))
    drive_2 = Drive(amplitude=ConstantWaveform(2.7, 0.2))
    device = AnalogDevice()

    program = QuantumProgram(register=register, drive=drive_1 >> drive_2)
    program.compile_to(device=device, device_max_duration_ratio=1.0)

    compiled_sequence = program.compiled_sequence
    compiled_sequence_repr = json.loads(compiled_sequence.to_abstract_repr())
    pulses_repr = [
        pulse for pulse in compiled_sequence_repr["operations"] if pulse["op"] == "pulse"
    ]
    assert len(pulses_repr) == 1
    assert compiled_sequence.get_duration() == device._max_duration


def test_compilation_same_phase_composition_with_short_segment() -> None:
    # a segment shorter than the channel min duration is fine when it is
    # part of a larger same-phase pulse
    register = Register(qubits={"q0": (0.0, 0.0)})
    short = Drive(amplitude=ConstantWaveform(0.01, 0.2))
    long = Drive(amplitude=ConstantWaveform(2.7, 0.2))

    program = QuantumProgram(register=register, drive=short >> long)
    program.compile_to(device=AnalogDevice())


@pytest.mark.parametrize("device", [AnalogDevice(), MockDevice()])
def test_compilation_different_phase_composition_has_extra_delay(
    device: Device,
) -> None:
    # on a device with phase_jump_time > 0, a phase change legitimately adds delay: this
    # models a real hardware constraint (the time it takes to change the phase between
    # consecutive pulses), so exceeding the idealized sum of segment durations is expected
    register = Register(qubits={"q0": (0.0, 0.0)})
    amp = ConstantWaveform(2.0, 0.2)
    det = ConstantWaveform(2.0, 0.0)
    drive_1 = Drive(amplitude=amp, detuning=det, phase=np.pi)
    drive_2 = Drive(amplitude=amp, detuning=det, phase=0.0)
    composite = drive_1 >> drive_2

    single_program = QuantumProgram(register=register, drive=drive_1)
    single_program.compile_to(device=device)
    single_duration = single_program.compiled_sequence.get_duration()

    composite_program = QuantumProgram(register=register, drive=composite)
    composite_program.compile_to(device=device)
    composite_duration = composite_program.compiled_sequence.get_duration()

    # MockDevice has phase_jump_time == 0, so the same assertion covers both
    # the "no delay" and "legitimate hardware delay" cases.
    phase_jump_time = device._device.channels["rydberg_global"].phase_jump_time
    assert composite_duration == 2 * single_duration + 2 * phase_jump_time
