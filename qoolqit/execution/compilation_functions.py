from __future__ import annotations

from pulser.pulse import Pulse as PulserPulse
from pulser.register.register import Register as PulserRegister
from pulser.sequence.sequence import Sequence as PulserSequence
from pulser.waveforms import CustomWaveform as PulserCustomWaveform

from qoolqit.devices import Device
from qoolqit.drive import Drive
from qoolqit.register import Register

from .utils import CompilerProfile


def _build_register(register: Register, device: Device, distance: float) -> PulserRegister:
    """Builds a Pulser Register from a QoolQit Register."""
    coords_qoolqit = register.qubits
    coords_pulser = {str(q): (distance * c[0], distance * c[1]) for q, c in coords_qoolqit.items()}
    pulser_register = PulserRegister(coords_pulser)
    if device._requires_layout:
        pulser_register = pulser_register.with_automatic_layout(device=device._device)
    return pulser_register


def _build_pulse(drive: Drive, converted_duration: int, time: float, energy: float) -> PulserPulse:
    """Builds a Pulser Pulse from a QoolQit Drive."""

    # Converted duration is an integer value in nanoseconds
    # Pulser requires a sample value for each nanosecond.
    time_array_pulser = list(range(converted_duration))

    # Convert each time step to the corresponding qoolqit value
    time_array_qoolqit = [t / time for t in time_array_pulser]

    # Evaluate the waveforms at each time step
    amp_values_qoolqit = drive.amplitude(time_array_qoolqit)
    det_values_qoolqit = drive.detuning(time_array_qoolqit)

    # Convert the waveform values
    amp_values_pulser = [amp * energy for amp in amp_values_qoolqit]
    det_values_pulser = [det * energy for det in det_values_qoolqit]

    amp_wf = PulserCustomWaveform(amp_values_pulser)
    det_wf = PulserCustomWaveform(det_values_pulser)

    return PulserPulse(amp_wf, det_wf, drive.phase)


def basic_compilation(
    register: Register,
    drive: Drive,
    device: Device,
    profile: CompilerProfile,
) -> PulserSequence:

    TARGET_DEVICE = device._device

    if profile == CompilerProfile.DEFAULT:
        TIME, ENERGY, DISTANCE = device.converter.factors
    elif profile == CompilerProfile.MAX_DURATION:
        TIME = (device._upper_duration) / drive.duration
        TIME, ENERGY, DISTANCE = device.converter.factors_from_time(TIME)
    elif profile == CompilerProfile.MAX_AMPLITUDE:
        ENERGY = (device._upper_amp) / drive.amplitude.max()
        TIME, ENERGY, DISTANCE = device.converter.factors_from_energy(ENERGY)
    elif profile == CompilerProfile.MIN_DISTANCE:
        DISTANCE = (device._lower_distance) / register.min_distance()
        TIME, ENERGY, DISTANCE = device.converter.factors_from_distance(DISTANCE)
    else:
        raise TypeError(f"Compiler profile {profile.value} requested but not implemented.")

    # Duration as multiple of clock period
    rounded_duration = int(drive.duration * TIME)
    cp = device._clock_period
    rm = rounded_duration % cp
    converted_duration = rounded_duration + (cp - rm) if rm != 0 else rounded_duration

    # Build pulse and register
    pulser_pulse = _build_pulse(drive, converted_duration, TIME, ENERGY)
    pulser_register = _build_register(register, device, DISTANCE)

    # Create sequence
    pulser_sequence = PulserSequence(pulser_register, TARGET_DEVICE)
    pulser_sequence.declare_channel("ising", "rydberg_global")
    pulser_sequence.add(pulser_pulse, "ising")

    return pulser_sequence
