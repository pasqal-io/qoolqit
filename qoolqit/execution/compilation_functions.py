from __future__ import annotations

import math
from enum import Enum

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


class CompilerProfile(Enum):
    """Enum for the different compilation profiles."""

    DEFAULT = "default"
    MAX_ENERGY = "max_energy"


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

    Requires the new time and energy scales set by the compilation.
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
    profile: CompilerProfile = CompilerProfile.DEFAULT,
) -> PulserSequence:
    """Compiles a QoolQit program to a PulserSequence.

    Defines:
    - program_energy_ratio: the ratio between the maximum amplitude in the drive
        and the maximum interaction energy.
    - device_energy_ratio: the ratio between the device's maximum allowed amplitude in the drive
        and the maximum possible interaction energy.

    If program_energy_ratio > device_energy_ratio the program is scaled to match the device's
    maximum allowed amplitude.
    Otherwise, the program is scaled to match the device's minimum allowed pairwise distance.

    If the device requires a layout, it is automatically generated.

    Args:
        register: QoolQit Register.
        drive: QoolQit Drive.
        device: QoolQit Device.

    Returns:
        PulserSequence: The compiled program as a pulser.Sequence object.
    """
    if profile == CompilerProfile.DEFAULT:
        TIME, ENERGY, DISTANCE = device.converter.factors
        _validate_program_default_profile(register, drive, device)
    elif profile == CompilerProfile.MAX_ENERGY:
        # fix compilation strategy according to the program energy ratio Ω_max/J_max
        program_energy_ratio = drive.amplitude.max() * register.min_distance() ** 6
        device_energy_ratio = device._energy_ratio
        if program_energy_ratio > device_energy_ratio:
            # map to the maximum amplitude allowed on the device
            ENERGY = device._upper_amp / drive.amplitude.max()
            # avoid round off precision issues
            ENERGY = math.floor(ENERGY * 1e12) / 1e12
            TIME, ENERGY, DISTANCE = device.converter.factors_from_energy(ENERGY)
        else:
            # map to the minimum pairwise distance allowed on the device
            DISTANCE = (device._lower_distance) / register.min_distance()
            TIME, ENERGY, DISTANCE = device.converter.factors_from_distance(DISTANCE)
        _validate_program_max_energy_profile(register, drive, device)
    else:
        raise ValueError(f"Invalid CompilerProfile: {profile}")

    # Build pulser pulse and register
    wf_converter = WaveformConverter(device=device, time=TIME, energy=ENERGY)
    pulser_amp_wf = wf_converter.convert(drive._amplitude)
    pulser_det_wf = wf_converter.convert(drive._detuning)
    pulser_pulse = PulserPulse(pulser_amp_wf, pulser_det_wf, drive.phase)

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
        if pulser_device.reusable_channels:
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


def _validate_program_default_profile(
    register: Register,
    drive: Drive,
    device: Device,
) -> None:
    """Validate that the program respect the device specs.

    Args:
        register: the register containing the qubits positions.
        drive: the drive acting on qubits, defining amplitude, detuning and phase.
        device: the selected device to compile to.

    Raises:
        CompilationError: if the compiled program does not respect the device specifications.
    """

    specs = device.specs

    max_amplitude = drive.amplitude.max()
    if specs["max_amplitude"] and (max_amplitude > specs["max_amplitude"]):
        msg = (
            f"The drive's maximum amplitude {max_amplitude:.3f} "
            "goes over the maximum value allowed for the chosen device:\n"
        )
        raise CompilationError(msg + f"{device}")

    max_abs_detuning = max(abs(drive.detuning.min()), abs(drive.detuning.max()))
    if specs["max_abs_detuning"] and (max_abs_detuning > specs["max_abs_detuning"]):
        msg = (
            f"The drive's maximum absolute detuning {max_abs_detuning:.4f} "
            "goes over the maximum value allowed for the chosen device:\n"
        )
        raise CompilationError(msg + f"{device}")

    duration = drive.duration
    if specs["max_duration"] and (duration > specs["max_duration"]):
        msg = (
            f"The drive's duration {duration:.4f} "
            "goes over the maximum value allowed for the chosen device:\n"
        )
        raise CompilationError(msg + f"{device}")

    if register.n_qubits > 1:
        min_distance = register.min_distance()
        if specs["min_distance"] and (min_distance < specs["min_distance"]):
            msg = (
                f"The register minimum distance between two qubits {min_distance:.4f} "
                "goes below the minimum allowed for the chosen device:\n"
            )
            raise CompilationError(msg + f"{device}")

    max_radial_distance = register.max_radial_distance()
    if specs["max_radial_distance"] and (max_radial_distance > specs["max_radial_distance"]):
        msg = (
            f"The register maximum radial distance {max_radial_distance:.4f} "
            "goes over the maximum allowed for the chosen device:\n"
        )
        raise CompilationError(msg + f"{device}")


def _validate_program_max_energy_profile(
    register: Register,
    drive: Drive,
    device: Device,
) -> None:
    """Validate that the program respect the given device specifications.

    Get the rescaling factors to scale the program to either
    the maximum allowed amplitude or minimum pairwise distance.
    Finally, check that the new values comply with the device specifications.

    Args:
        register: the register containing the qubits positions.
        drive: the drive acting on qubits, defining amplitude, detuning and phase.
        device: the selected device to compile to.

    Raises:
        CompilationError: if the compiled program does not respect the device specifications.
    """

    # Get profile factors in the adimensional basis, not conversion factors to pulser
    # these factors respect ΔE*ΔT=1 and ΔE*ΔR^6=1 invariants
    # this part can be removed when compilation return a QuantumProgram that can be directly checked
    program_energy_ratio = drive.amplitude.max() * register.min_distance() ** 6
    device_energy_ratio = device._energy_ratio
    specs = device.specs
    # fix compilation strategy according to the program energy ratio Ω_max/J_max
    if program_energy_ratio > device_energy_ratio:
        ENERGY = device._target_amplitude / drive.amplitude.max()
        TIME, DISTANCE = 1 / ENERGY, ENERGY ** (-1 / 6)
    else:
        DISTANCE = device._target_distance / register.min_distance()
        TIME, ENERGY = DISTANCE**6, 1 / DISTANCE**6

    max_amplitude = drive.amplitude.max() * ENERGY
    if specs["max_amplitude"]:
        if max_amplitude > specs["max_amplitude"]:
            msg = (
                f"The MAX_ENERGY profile unexpectedly failed to meet the device specifications.\n"
                f"The target {max_amplitude=} goes over the maximum value allowed for the device:\n"
            )
            raise CompilationError(msg + f"{device}")

    min_distance = register.min_distance() * DISTANCE
    if specs["min_distance"]:
        if min_distance < specs["min_distance"]:
            msg = (
                f"The MAX_ENERGY profile unexpectedly failed to meet the device specifications.\n"
                f"The target {min_distance=} goes below the minimum value allowed for the device:\n"
            )
            raise CompilationError(msg + f"{device}")

    max_abs_detuning = max(abs(drive.detuning.min()), abs(drive.detuning.max()))
    if specs["max_abs_detuning"]:
        max_abs_detuning_to_compile = specs["max_abs_detuning"] / ENERGY
        if max_abs_detuning > max_abs_detuning_to_compile:
            msg = (
                "After rescaling the input program to MAX_ENERGY, the drive's maximum absolute "
                "detuning went over the maximum value allowed for the selected device.\n"
                "To successfully compile your program, set the "
                f"maximum absolute detuning below {max_abs_detuning_to_compile}"
            )
            raise CompilationError(msg)

    duration = drive.duration
    if specs["max_duration"]:
        max_duration_to_compile = specs["max_duration"] / TIME
        if duration > max_duration_to_compile:
            msg = (
                f"After rescaling the input program to MAX_ENERGY, the drive's duration "
                f"{duration:.4f} goes over the maximum value allowed for the selected device:\n"
                "To successfully compile your program, set the "
                f"maximum duration below {max_duration_to_compile}"
            )
            raise CompilationError(msg)

    max_radial_distance = register.max_radial_distance()
    if specs["max_radial_distance"]:
        max_radial_distance_to_compile = specs["max_radial_distance"] / DISTANCE
        if max_radial_distance > max_radial_distance_to_compile:
            msg = (
                f"After rescaling the input program to MAX_ENERGY, the register's maximum radial "
                f"distance {max_radial_distance:.4f} goes over the maximum value allowed for the "
                "selected device:\n"
                "To successfully compile your program, set the "
                f"maximum radial distance below {max_radial_distance_to_compile}"
            )
            raise CompilationError(msg)
