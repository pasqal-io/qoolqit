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
from qoolqit.exceptions import CompilationError
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


class WaveformConverter:
    """Convert a QoolQit waveform into a equivalent Pulser waveform.

    Requires the new time and energy scales set by the compilation profile.
    Additionally, requires the clock period of the device to round the duration.
    """

    def __init__(self, device: Device, time: float, energy: float):
        self._time = time
        self._energy = energy
        self._clock_period = device._clock_period

    def _pulser_duration(self, waveform: Waveform) -> int:
        """Return the new duration of the converted pulser waveform."""
        converted_duration = round(waveform.duration * self._time)
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

    program_max_amplitude = drive.amplitude.max()
    program_min_distance = register.min_distance()
    program_energy_ratio = program_max_amplitude * program_min_distance**6

    device_energy_ratio = device._energy_ratio
    if device_energy_ratio:
        if program_energy_ratio > device_energy_ratio:
            # fallback to MAX_AMPLITUDE
            if profile == CompilerProfile.MIN_DISTANCE:
                profile = CompilerProfile.MAX_AMPLITUDE
        else:
            # fallback to MIN_DISTANCE
            if profile == CompilerProfile.MAX_AMPLITUDE:
                profile = CompilerProfile.MIN_DISTANCE

    _validate_program(register, drive, device, profile)

    # strategies are applied only if the device has the corresponding extrema value
    if profile == CompilerProfile.DEFAULT:
        TIME, ENERGY, DISTANCE = device.converter.factors
    elif (profile == CompilerProfile.MAX_DURATION) and device._max_duration:
        TIME = (device._max_duration) / drive.duration
        TIME, ENERGY, DISTANCE = device.converter.factors_from_time(TIME)
    elif (profile == CompilerProfile.MAX_AMPLITUDE) and device._max_amp:
        ENERGY = (device._max_amp) / drive.amplitude.max()
        TIME, ENERGY, DISTANCE = device.converter.factors_from_energy(ENERGY)
        # round up/down to avoid round-off errors
        if ENERGY > 1:
            ENERGY = math.floor(1e12 * ENERGY) / 1e12
    elif (profile == CompilerProfile.MIN_DISTANCE) and (device._min_distance > 0.0):
        DISTANCE = (device._min_distance) / register.min_distance()
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
    pulser_device = device._device
    pulser_sequence = PulserSequence(pulser_register, pulser_device)
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


def _validate_program(
    register: Register,
    drive: Drive,
    device: Device,
    profile: CompilerProfile,
) -> None:
    """Validate that the program respect the given device specifications.

    Get the rescaling factors from different compilation strategies still in the
    adimensional frame. The default compilation just preserve ratios.
    Then compute the new properties of the program:
        - maximum drive amplitude
        - drive duration
        - register minimum distance between qubits
        - register maximum radial distance
    Finally, check that the new values comply with the device specifications.

    Args:
        register: the register containing the qubits positions.
        drive: the drive acting on qubits, defining amplitude, detuning and phase.
        device: the selected device to compile to.
        profile: the compilation strategy.

    Raises:
        CompilationError: if the compiled program does not respect the device specifications.
    """
    specs = device.specs

    # Get profile factors in the adimensional basis, not conversion factors to pulser
    # these factors respect ΔE*ΔT=1 and ΔE*ΔR^6=1 invariants
    # this part can be removed when compilation return a QuantumProgram that can be directly checked
    if profile == CompilerProfile.DEFAULT:
        TIME, ENERGY, DISTANCE = 1.0, 1.0, 1.0
    elif (profile == CompilerProfile.MAX_DURATION) and specs["max_duration"]:
        TIME = specs["max_duration"] / drive.duration
        TIME, ENERGY, DISTANCE = TIME, 1 / TIME, TIME ** (1 / 6)
    elif (profile == CompilerProfile.MAX_AMPLITUDE) and specs["max_amplitude"]:
        ENERGY = specs["max_amplitude"] / drive.amplitude.max()
        TIME, ENERGY, DISTANCE = 1 / ENERGY, ENERGY, ENERGY ** (-1 / 6)
    elif (profile == CompilerProfile.MIN_DISTANCE) and specs["min_distance"]:
        DISTANCE = specs["min_distance"] / register.min_distance()
        TIME, ENERGY, DISTANCE = DISTANCE**6, 1 / DISTANCE**6, DISTANCE
    else:
        raise CompilationError(
            f"Compiler profile {profile.value} cannot be used with {device.name} "
            f"because the target min/max value is not specified in the chosen device: \n {device}"
        )

    device_specs_msg = f"{device}"

    max_amplitude = drive.amplitude.max() * ENERGY
    if specs["max_amplitude"] and (max_amplitude > specs["max_amplitude"]):
        msg = (
            f"The drive's maximum amplitude {max_amplitude} "
            "goes over the maximum value allowed for the chosen device:\n."
        )
        raise CompilationError(msg + device_specs_msg)

    max_abs_detuning = max(abs(drive.detuning.min()), abs(drive.detuning.max())) * ENERGY
    if specs["max_abs_detuning"] and (max_abs_detuning > specs["max_abs_detuning"]):
        msg = (
            f"The drive's maximum absolute detuning {max_abs_detuning} "
            "goes over the maximum value allowed for the chosen device:\n."
        )
        raise CompilationError(msg + device_specs_msg)

    duration = drive.duration * TIME
    if specs["max_duration"] and (duration > specs["max_duration"]):
        msg = (
            f"The drive's duration {duration} "
            "goes over the maximum value allowed for the chosen device:\n"
        )
        raise CompilationError(msg + device_specs_msg)

    if register.n_qubits > 1:
        min_distance = register.min_distance() * DISTANCE
        if specs["min_distance"] and (min_distance < specs["min_distance"]):
            msg = (
                f"The register minimum distance between two qubits {min_distance} "
                "goes below the minimum allowed for the chosen device:\n"
            )
            raise CompilationError(msg + device_specs_msg)

    max_radial_distance = register.max_radial_distance() * DISTANCE
    if specs["max_radial_distance"] and (max_radial_distance > specs["max_radial_distance"]):
        msg = (
            f"The register maximum radial distance {max_radial_distance} "
            "goes over the maximum allowed for the chosen device:\n"
        )
        raise CompilationError(msg + device_specs_msg)
