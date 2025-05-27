from __future__ import annotations

from pulser import CustomWaveform as PulserCustomWaveform
from pulser import Pulse as PulserPulse
from pulser import Register as PulserRegister
from pulser import Sequence as PulserSequence

from qoolqit.devices import AnalogDevice, Device, MockDevice
from qoolqit.register import Register
from qoolqit.sequence import Sequence

from .utils import CompilerProfile


def compile_to_mock_device(
    register: Register,
    sequence: Sequence,
    device: Device,
    profile: CompilerProfile,
) -> PulserSequence:

    TARGET_DEVICE = MockDevice._device

    if profile == CompilerProfile.DEFAULT:
        TIME, ENERGY, DISTANCE = device.unit_converter.factors
    else:
        raise NotImplementedError(
            f"The requested compilation profile is not implemented for device {device.name}"
        )

    converted_duration = int(sequence.duration * TIME + 1)

    time_array_pulser = list(range(converted_duration))

    time_array_qoolqit = [t / TIME for t in time_array_pulser]

    amp_values_qoolqit = sequence.amplitude(time_array_qoolqit)
    det_values_qoolqit = sequence.detuning(time_array_qoolqit)

    amp_values_pulser = [amp * ENERGY for amp in amp_values_qoolqit]  # type: ignore [union-attr]
    det_values_pulser = [det * ENERGY for det in det_values_qoolqit]  # type: ignore [union-attr]

    coords_qoolqit = register.qubits
    coords_pulser = {q: DISTANCE * c for q, c in coords_qoolqit.items()}

    pulser_register = PulserRegister(coords_pulser)
    pulser_sequence = PulserSequence(pulser_register, TARGET_DEVICE)
    pulser_sequence.declare_channel("ising", "rydberg_global")

    amp_wf = PulserCustomWaveform(amp_values_pulser)
    det_wf = PulserCustomWaveform(det_values_pulser)

    pulse = PulserPulse(amp_wf, det_wf, 0.0)

    pulser_sequence.add(pulse, "ising")

    return pulser_sequence


def compile_to_analog_device(
    register: Register,
    sequence: Sequence,
    device: Device,
    profile: CompilerProfile,
) -> PulserSequence:

    TARGET_DEVICE = AnalogDevice._device

    if profile == CompilerProfile.DEFAULT:
        TIME, ENERGY, DISTANCE = device.unit_converter.factors
    else:
        raise NotImplementedError(
            f"The requested compilation profile is not implemented for device {device.name}"
        )

    converted_duration = sequence.duration * TIME
    rounded_duration = int(converted_duration) + 1
    remainder = rounded_duration % 4
    converted_duration = rounded_duration + (4 - remainder) if remainder != 0 else rounded_duration

    time_array_pulser = list(range(converted_duration))

    time_array_qoolqit = [t / TIME for t in time_array_pulser]

    amp_values_qoolqit = sequence.amplitude(time_array_qoolqit)
    det_values_qoolqit = sequence.detuning(time_array_qoolqit)

    amp_values_pulser = [amp * ENERGY for amp in amp_values_qoolqit]  # type: ignore [union-attr]
    det_values_pulser = [det * ENERGY for det in det_values_qoolqit]  # type: ignore [union-attr]

    coords_qoolqit = register.qubits
    coords_pulser = {q: DISTANCE * c for q, c in coords_qoolqit.items()}

    pulser_register = PulserRegister(coords_pulser)
    pulser_sequence = PulserSequence(pulser_register, TARGET_DEVICE)
    pulser_sequence.declare_channel("ising", "rydberg_global")

    amp_wf = PulserCustomWaveform(amp_values_pulser)
    det_wf = PulserCustomWaveform(det_values_pulser)

    pulse = PulserPulse(amp_wf, det_wf, 0.0)

    pulser_sequence.add(pulse, "ising")

    return pulser_sequence
