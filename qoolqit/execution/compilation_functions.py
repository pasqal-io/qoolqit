from __future__ import annotations

import math

from pulser.devices import Device as PulserDevice
from pulser.parametrized import ParamObj
from pulser.pulse import Pulse as PulserPulse
from pulser.register.register import Register as PulserRegister
from pulser.sequence.sequence import Sequence as PulserSequence
from pulser.waveforms import Waveform as PulserWaveform

from qoolqit.devices import Device
from qoolqit.drive import Drive, Waveform, WeightedDetuning
from qoolqit.register import Register

from .utils import CompilerProfile


def _build_register(register: Register, device: Device, distance: float) -> PulserRegister:
    """Builds a Pulser Register from a QoolQit Register."""
    coords_qoolqit = register.qubits
    coords_pulser = {str(q): (distance * c[0], distance * c[1]) for q, c in coords_qoolqit.items()}
    pulser_register = PulserRegister(coords_pulser)
    if device._requires_layout:
        assert isinstance(device._device, PulserDevice)
        pulser_register = pulser_register.with_automatic_layout(device=device._device)
    return pulser_register


class QuantumProgramCompilationError(ValueError):
    """An error encountered while compiling a QuantumProgram."""

    ...


class WeightedDetuningWaveformError(QuantumProgramCompilationError):
    """An error encountered while compiling the waveform of a WeightedDetuning."""

    ...


class WaveformConverter:
    """Convert a QoolQit waveform into a equivalent Pulser waveform.

    Requires the new time and energy scales set by the compilation profile.
    Additionaly, requires the clock period fo the device to round the duration.
    """

    def __init__(self, device: Device, time: float, energy: float):
        self._time = time
        self._energy = energy
        self._clock_period = device._clock_period

    def _pulser_duration(self, waveform: Waveform) -> int:
        """Return the new duration of the converted pulser waveform."""
        converted_duration = int(waveform.duration * self._time)
        cp = self._clock_period
        rm = converted_duration % cp
        pulser_duration = converted_duration + (cp - rm) if rm != 0 else converted_duration
        return pulser_duration

    def convert(self, waveform: Waveform) -> ParamObj | PulserWaveform:
        """Convert a QoolQit waveform into a equivalent Pulser waveform."""
        pulser_duration = self._pulser_duration(waveform)
        return waveform._to_pulser(duration=pulser_duration) * self._energy


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
        # round up/down to avoid roundoff errors
        if ENERGY > 1:
            ENERGY = math.floor(1e12 * ENERGY) / 1e12
    elif profile == CompilerProfile.MIN_DISTANCE:
        DISTANCE = (device._lower_distance) / register.min_distance()
        TIME, ENERGY, DISTANCE = device.converter.factors_from_distance(DISTANCE)
    else:
        raise TypeError(f"Compiler profile {profile.value} requested but not implemented.")

    wf_converter = WaveformConverter(device=device, time=TIME, energy=ENERGY)

    # Build pulser pulse and register
    amp_wf = wf_converter.convert(drive._amplitude)
    det_wf = wf_converter.convert(drive._detuning)
    pulser_pulse = PulserPulse(amp_wf, det_wf, drive.phase)

    pulser_register = _build_register(register, device, DISTANCE)

    # Create sequence
    pulser_sequence = PulserSequence(pulser_register, TARGET_DEVICE)
    pulser_sequence.declare_channel("rydberg", "rydberg_global")
    pulser_sequence.add(pulser_pulse, "rydberg")

    if len(drive.weighted_detunings) > 0:
        # Add detuning map
        channels = list(device._device.dmm_channels.keys())
        if len(channels) == 0:
            raise ValueError(
                f"This program specifies {len(drive.weighted_detunings)} detunings but "
                "the device doesn't offer any DMM channel to execute them."
            )

        detuning_adder = _DetuningAdder(wf_converter, pulser_register, pulser_sequence)

        # If our device supports reusable channels, we can declare multiple
        # DMM channels with the same specs
        if device._device.reusable_channels:
            # Arbitrarily pick the first channel.
            dmm_id = channels[0]
            for detuning in drive.weighted_detunings:
                detuning_adder.add_detuning(dmm_id, detuning)
        # Do we have enough channels for our detunings?
        elif len(channels) >= len(drive.weighted_detunings):
            for dmm_id, detuning in zip(channels, drive.weighted_detunings):
                detuning_adder.add_detuning(dmm_id, detuning)
        else:
            raise ValueError(
                f"This program specifies {len(drive.weighted_detunings)} detunings but "
                f"the device only offers {len(channels)} DMM channels to execute them."
            )

    return pulser_sequence


class _DetuningAdder:
    def __init__(
        self,
        wf_converter: WaveformConverter,
        pulser_register: PulserRegister,
        pulser_sequence: PulserSequence,
    ):
        self._wf_converter = wf_converter
        self._pulser_register = pulser_register
        self._pulser_sequence = pulser_sequence

    def add_detuning(self, dmm_id: str, detuning: WeightedDetuning) -> None:
        # conversion may be needed for pulser register as only str keys are accepted
        converted_weights = {
            k if isinstance(k, str) else str(k): v for k, v in detuning.weights.items()
        }
        detuning_map = self._pulser_register.define_detuning_map(detuning_weights=converted_weights)
        self._pulser_sequence.config_detuning_map(detuning_map, dmm_id=dmm_id)
        waveform = self._wf_converter.convert(detuning.waveform)
        self._pulser_sequence.add_dmm_detuning(waveform, dmm_id)
