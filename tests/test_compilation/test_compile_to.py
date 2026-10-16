"""Test compilation independently on the compilation profiles."""

from __future__ import annotations

from typing import Literal
from unittest.mock import MagicMock

import numpy as np
import pytest
from pulser import AnalogDevice as PulserAnalogDevice
from pulser.sampler import sample

from qoolqit import (
    AnalogDevice,
    AnalogDeviceWithDMM,
    Drive,
    MockDevice,
    QuantumProgram,
    Register,
)
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


@pytest.mark.parametrize("profile", [CompilerProfile.MAX_ENERGY, CompilerProfile.DEFAULT])
def test_compilation_with_several_dmms(profile: CompilerProfile) -> None:
    """Test that each DMM of the drive compiles to its own detuning map."""
    register = Register(qubits={"q0": (0.0, 0.7), "q1": (-0.5, -0.5), "q2": (0.5, -0.5)})

    amplitude = ConstantWaveform(5.0, 0.5)
    detuning = ConstantWaveform(5.0, -1.0)
    dmm_1 = DetuningMapModulator(
        waveform=ConstantWaveform(5.0, -1.0), weights={"q0": 0.1, "q1": 0.2, "q2": 0.9}
    )
    dmm_2 = DetuningMapModulator(
        waveform=ConstantWaveform(5.0, -0.5), weights={"q0": 1.0, "q2": 0.3}
    )
    drive = Drive(amplitude=amplitude, detuning=detuning, dmm=[dmm_1, dmm_2])
    program = QuantumProgram(register=register, drive=drive)
    program.compile_to(device=MockDevice(), profile=profile)

    pulser_sequence = program.compiled_sequence
    assert list(pulser_sequence.declared_channels) == ["rydberg", "dmm_0", "dmm_0_1"]

    samples = sample(pulser_sequence)
    global_det = samples.channel_samples["rydberg"].det
    dmm_0 = samples.channel_samples["dmm_0"]
    dmm_0_1 = samples.channel_samples["dmm_0_1"]
    assert dmm_0.detuning_map.weights == (0.1, 0.2, 0.9)
    assert dmm_0_1.detuning_map.weights == (1.0, 0.3)
    np.testing.assert_allclose(dmm_0.det, global_det, atol=1e-8)
    np.testing.assert_allclose(dmm_0_1.det, 0.5 * global_det, atol=1e-8)

    # each qubit sees δ + Σₖ εᵢₖ Δₖ, with δ = Δ₁ = 2 Δ₂
    local = samples.to_nested_dict(all_local=True)["Local"]["ground-rydberg"]
    for qid, factor in {"q0": 1.6, "q1": 1.2, "q2": 2.05}.items():
        np.testing.assert_allclose(local[qid]["det"], factor * global_det, atol=1e-8)


def test_compilation_with_one_dmm_in_a_list() -> None:
    """Test that a single DMM compiles the same, given alone or in a list."""
    register = Register(qubits={"q0": (0.0, 0.7), "q1": (-0.5, -0.5)})
    amplitude = ConstantWaveform(5.0, 0.1)
    dmm = DetuningMapModulator(waveform=ConstantWaveform(5.0, -1.0), weights={"q0": 0.4})

    sequences = []
    for dmm_arg in (dmm, [dmm]):
        program = QuantumProgram(register, Drive(amplitude=amplitude, dmm=dmm_arg))
        program.compile_to(device=AnalogDeviceWithDMM())
        sequences.append(program.compiled_sequence.to_abstract_repr())
    assert sequences[0] == sequences[1]


def test_several_dmms_not_supported() -> None:
    """Test that several DMMs need a device that can reuse its DMM channel."""
    register = Register(qubits={"q0": (0.0, 0.0)})
    dmm = DetuningMapModulator(waveform=ConstantWaveform(5.0, -0.1), weights={"q0": 1.0})
    drive = Drive(amplitude=ConstantWaveform(5.0, 0.1), dmm=[dmm, dmm])
    program = QuantumProgram(register=register, drive=drive)
    with pytest.raises(CompilationError, match="does not allow reusing its DMM channel"):
        program.compile_to(device=AnalogDeviceWithDMM())


def test_compile_to_wrong_device_type() -> None:
    """Test compilation to a device with a different type."""
    register = Register(qubits={"q0": (0.0, 0.0)})
    drive = Drive(amplitude=ConstantWaveform(2.0, 0.2))
    program = QuantumProgram(register=register, drive=drive)
    with pytest.raises(TypeError, match="`device` must be of type `qoolqit.devices.Device`."):
        program.compile_to(device="I'm not a device")  # type: ignore [arg-type]
    with pytest.raises(TypeError, match="`device` must be of type `qoolqit.devices.Device`."):
        program.compile_to(device=PulserAnalogDevice)  # type: ignore [arg-type]
