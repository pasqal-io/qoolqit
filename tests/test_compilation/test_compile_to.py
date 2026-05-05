"""Test compilation independently on the compilation profiles."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest
from pulser.sampler import sample

from qoolqit import AnalogDevice, Constant, Drive, MockDevice, QuantumProgram, Register
from qoolqit.drive import DetuningMapModulator
from qoolqit.exceptions import CompilationError
from qoolqit.execution.compilation_functions import CompilerProfile


@pytest.mark.parametrize("profile", [CompilerProfile.MAX_ENERGY, CompilerProfile.WORKING_POINT])
def test_compilation_single_qubit(profile: CompilerProfile) -> None:
    """Test compilation of a single-qubit program."""
    register = Register(qubits={"q0": (0.0, 0.0)})
    drive = Drive(amplitude=Constant(2.0, 0.2))
    program = QuantumProgram(register=register, drive=drive)

    # Test compilation on the default profile
    program.compile_to(device=AnalogDevice(), profile=profile)
    assert program.is_compiled


def test_dmm_not_supported() -> None:
    """Test compilation of a program with a DMM but the device does not support it."""
    mock_register = MagicMock(spec=Register)
    mock_dmm = MagicMock(spec=DetuningMapModulator, weights={})
    mock_drive = MagicMock(spec=Drive, dmm=mock_dmm)
    program = QuantumProgram(register=mock_register, drive=mock_drive)
    with pytest.raises(CompilationError, match="The device does not support DMM"):
        # AnalogDevice does not support DMM
        program.compile_to(device=AnalogDevice())


@pytest.mark.parametrize("profile", [CompilerProfile.MAX_ENERGY, CompilerProfile.WORKING_POINT])
def test_compilation_with_dmm(profile: CompilerProfile) -> None:
    """Test compilation of a program with a DMM."""
    register = Register(qubits={"q0": (0.0, 0.7), "q1": (-0.5, -0.5), "q2": (0.5, -0.5)})

    amplitude = Constant(5.0, 0.5)
    detuning = Constant(5.0, -1.23)
    dmm = DetuningMapModulator(
        waveform=Constant(5.0, -1.23), weights={"q0": 0.1, "q1": 0.2, "q2": 0.9}
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
