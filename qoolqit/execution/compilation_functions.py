from __future__ import annotations

from pulser import CustomWaveform as PulserCustomWaveform
from pulser import Pulse as PulserPulse
from pulser import Register as PulserRegister
from pulser import Sequence as PulserSequence

from qoolqit.devices import Device
from qoolqit.register import Register
from qoolqit.sequence import Sequence

from .utils import CompilerProfile


def _build_register(register: Register, distance: float) -> PulserRegister:
    """Builds a Pulser Register from a QoolQit Register."""
    coords_qoolqit = register.qubits
    coords_pulser = {q: distance * c for q, c in coords_qoolqit.items()}
    return PulserRegister(coords_pulser)


def _build_pulse(
    sequence: Sequence, converted_duration: int, time: float, energy: float
) -> PulserPulse:
    """Builds a Pulser Pulse from a QoolQit Sequence."""

    # Converted duration is an integer value in nanoseconds
    # Pulser requires a sample value for each nanosecond.
    time_array_pulser = list(range(converted_duration))

    # Convert each time step to the corresponding qoolqit value
    time_array_qoolqit = [t / time for t in time_array_pulser]

    # Evaluate the waveforms at each time step
    amp_values_qoolqit = sequence.amplitude(time_array_qoolqit)
    det_values_qoolqit = sequence.detuning(time_array_qoolqit)

    # Convert the waveform values
    amp_values_pulser = [amp * energy for amp in amp_values_qoolqit]  # type: ignore [union-attr]
    det_values_pulser = [det * energy for det in det_values_qoolqit]  # type: ignore [union-attr]

    amp_wf = PulserCustomWaveform(amp_values_pulser)
    det_wf = PulserCustomWaveform(det_values_pulser)

    return PulserPulse(amp_wf, det_wf, sequence.phase)


def compile_to_mock_device(
    register: Register,
    sequence: Sequence,
    device: Device,
    profile: CompilerProfile,
) -> PulserSequence:

    TARGET_DEVICE = device._device

    if profile == CompilerProfile.DEFAULT:
        TIME, ENERGY, DISTANCE = device.converter.factors
    if profile == CompilerProfile.MAX_DURATION:
        TIME = (device._max_duration) / sequence.duration
        TIME, ENERGY, DISTANCE = device.converter.factors_from_time(TIME)

    converted_duration = int(sequence.duration * TIME)

    pulser_pulse = _build_pulse(sequence, converted_duration, TIME, ENERGY)
    pulser_register = _build_register(register, DISTANCE)

    pulser_sequence = PulserSequence(pulser_register, TARGET_DEVICE)
    pulser_sequence.declare_channel("ising", "rydberg_global")
    pulser_sequence.add(pulser_pulse, "ising")

    return pulser_sequence


def compile_to_analog_device(
    register: Register,
    sequence: Sequence,
    device: Device,
    profile: CompilerProfile,
) -> PulserSequence:

    TARGET_DEVICE = device._device

    if profile == CompilerProfile.DEFAULT:
        TIME, ENERGY, DISTANCE = device.converter.factors
    if profile == CompilerProfile.MAX_DURATION:
        TIME = (device._max_duration) / sequence.duration
        TIME, ENERGY, DISTANCE = device.converter.factors_from_time(TIME)

    rounded_duration = int(sequence.duration * TIME)
    remainder = rounded_duration % 4
    converted_duration = rounded_duration + (4 - remainder) if remainder != 0 else rounded_duration

    pulser_pulse = _build_pulse(sequence, converted_duration, TIME, ENERGY)
    pulser_register = _build_register(register, DISTANCE)

    pulser_sequence = PulserSequence(pulser_register, TARGET_DEVICE)
    pulser_sequence.declare_channel("ising", "rydberg_global")
    pulser_sequence.add(pulser_pulse, "ising")

    return pulser_sequence
