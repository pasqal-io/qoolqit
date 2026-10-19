"""Test compilation independently on the compilation profiles."""

from __future__ import annotations

from typing import Literal
from unittest.mock import MagicMock

import numpy as np
import pytest
from pulser import AnalogDevice as PulserAnalogDevice
from pulser.sampler import sample
from scipy.integrate import quad

from qoolqit import AnalogDevice, Device, Drive, MockDevice, QuantumProgram, Register
from qoolqit.drive import DetuningMapModulator
from qoolqit.exceptions import CompilationError
from qoolqit.execution.compilation_functions import CompilerProfile, _WaveformConverter
from qoolqit.waveforms import (
    BlackmanWaveform,
    ConstantWaveform,
    InterpolatedWaveform,
    PiecewiseLinearWaveform,
    RampWaveform,
    Waveform,
)


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


@pytest.mark.parametrize("device", [AnalogDevice(), MockDevice()])
@pytest.mark.parametrize("profile", [CompilerProfile.DEFAULT, CompilerProfile.MAX_ENERGY])
@pytest.mark.parametrize(
    "waveform", [BlackmanWaveform(100.0, area=0.3), ConstantWaveform(100.0, 0.003)]
)
def test_amplitude_area_is_kept_by_compilation(
    device: Device, profile: CompilerProfile, waveform: Waveform
) -> None:
    """The pulse area Ω·t is unit-free: compiling keeps it, whatever the waveform type.

    This also checks that each profile pairs its time and energy units so that
    time × energy = 1000.
    """
    # At a minimum distance of 1, MAX_ENERGY would pick the same units as DEFAULT; at 1.1 it
    # maps the register to the device's minimum distance with units of its own.
    register = Register(qubits={"q0": (0.0, 0.0), "q1": (1.1, 0.0)})
    program = QuantumProgram(register=register, drive=Drive(amplitude=waveform))
    program.compile_to(device=device, profile=profile)

    # Pulses can't be read back from a compiled Sequence, so summing the sampled amplitude
    # (rad/µs, 1 ns steps) is the only way to get the pulser area here.
    amp = sample(program.compiled_sequence).channel_samples["rydberg"].amp
    pulser_area = np.sum(amp) / 1000

    # Budget: these samples are exact (a constant, or pulser's Blackman normalized to its
    # area), so the only error is the duration rounding: up to 3.5 ns on AnalogDevice (4 ns
    # clock) and 0.5 ns on MockDevice (1 ns clock). The shortest pulses here last 1018.8 and
    # 162.7 ns (MAX_ENERGY), so the area changes by at most 3.4e-3 and 3.1e-3 (measured over
    # all cases: 1.7e-3 at most). A Blackman 1% too strong or too weak fails.
    expected_area, _ = quad(waveform, 0, waveform.duration)
    assert pulser_area == pytest.approx(expected_area, rel=5e-3, abs=0)


@pytest.mark.parametrize("device", [AnalogDevice(), MockDevice()])
@pytest.mark.parametrize(
    ("energy", "rel"),
    [
        # 1000 / energy * 50 ns is a whole number of clock periods (4 ns on AnalogDevice, 1 ns
        # on MockDevice), and so is every composite segment: no rounding. Budget: quad's own
        # error estimate, up to 3.2e-8 for the composite with a jump; float64 sums of up to
        # 1000 samples ~1e-13 (measured: 8.4e-14 at most).
        (50.0, 1e-7),
        (125.0, 1e-7),
        (250.0, 1e-7),
        # The duration is rounded to the clock and the composite segments to 1 ns. Budget,
        # measured over the cases below: 1.7e-3 at most (904 instead of 902.4 ns on
        # AnalogDevice at 55.4063).
        (55.4063, 3e-3),
        (347.0, 3e-3),
        (33.3, 3e-3),
    ],
)
@pytest.mark.parametrize(
    "waveform",
    [
        ConstantWaveform(50.0, 0.006),
        RampWaveform(50.0, 0.0, 0.012),
        BlackmanWaveform(50.0, area=0.3),
        PiecewiseLinearWaveform([20.0, 30.0], [0.0, 0.01, 0.0]),
        ConstantWaveform(20.0, 0.005) >> BlackmanWaveform(30.0, area=0.2),
    ],
)
def test_converter_keeps_area(device: Device, waveform: Waveform, energy: float, rel: float) -> None:
    """Every waveform type keeps its area through `_WaveformConverter.convert`."""
    converter = _WaveformConverter(device, time=1000 / energy, energy=energy)
    # pulser's Waveform.integral sums the 1 ns samples (rad/µs) times 1e-3: the area in rad
    converted_area = converter.convert(waveform).integral
    expected_area, _ = quad(waveform, 0, waveform.duration)
    assert converted_area == pytest.approx(expected_area, rel=rel, abs=0)


@pytest.mark.parametrize("device", [AnalogDevice(), MockDevice()])
@pytest.mark.parametrize("energy", [50.0, 125.0, 250.0, 55.4063, 347.0, 33.3])
def test_converter_keeps_interpolated_area(device: Device, energy: float) -> None:
    """Same contract as `test_converter_keeps_area`, with a looser budget of its own."""
    waveform = InterpolatedWaveform(50.0, [0.0, 0.008, 0.004, 0.0])
    converter = _WaveformConverter(device, time=1000 / energy, energy=energy)
    converted_area = converter.convert(waveform).integral
    expected_area, _ = quad(waveform, 0, waveform.duration)
    # Budget: pulser spreads the interpolated curve over N - 1 ns for an N ns waveform, so its
    # area is short by 1/N: 6.9e-3 for the shortest pulse here (144 ns at energy 347), plus the
    # duration rounding as above (measured worst: 7.6e-3). This tolerance can't see a
    # sub-percent error on InterpolatedWaveform; a doubled amplitude still fails.
    assert converted_area == pytest.approx(expected_area, rel=1e-2, abs=0)
