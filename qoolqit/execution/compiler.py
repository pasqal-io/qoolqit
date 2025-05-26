from __future__ import annotations

from pulser import CustomWaveform as PulserCustomWaveform
from pulser import Pulse as PulserPulse
from pulser import Sequence as PulserSequence
from pulser import register as PulserRegister
from pulser.devices._device_datacls import BaseDevice as PulserDevice

from qoolqit.devices import Device
from qoolqit.quantum_program import QuantumProgram

from .convert import UnitConverter


class Compiler:

    def __init__(self, program: QuantumProgram, device: Device):

        self._program = program
        self._device = device

        self._target_device = device._device
        self._converter = UnitConverter(device)

    @property
    def target_device(self) -> PulserDevice:
        return self._target_device

    @property
    def converter(self) -> UnitConverter:
        return self._converter

    @property
    def program(self) -> QuantumProgram:
        return self._program

    def set_energy_unit(self, energy: float) -> None:
        self._converter.set_energy_unit(energy)

    def set_distance_unit(self, energy: float) -> None:
        self._converter.set_distance_unit(energy)

    def compile(self) -> PulserSequence:

        TIME, ENERGY, DISTANCE = self.converter.factors

        sequence = self.program.sequence
        register = self.program.register

        converted_duration = sequence.duration * TIME

        time_array_pulser = list(range(int(converted_duration) + 1))

        time_array_qoolqit = [t / TIME for t in time_array_pulser]

        amp_values_qoolqit = sequence.amplitude(time_array_qoolqit)
        det_values_qoolqit = sequence.detuning(time_array_qoolqit)

        amp_values_pulser = [amp * ENERGY for amp in amp_values_qoolqit]  # type: ignore [union-attr]
        det_values_pulser = [det * ENERGY for det in det_values_qoolqit]  # type: ignore [union-attr]

        coords_qoolqit = register.qubits
        coords_pulser = {q: DISTANCE * c for q, c in coords_qoolqit.items()}

        pulser_device = self.target_device
        pulser_register = PulserRegister(coords_pulser)
        pulser_sequence = PulserSequence(pulser_register, pulser_device)
        pulser_sequence.declare_channel("ising", "rydberg_global")

        amp_wf = PulserCustomWaveform(amp_values_pulser)
        det_wf = PulserCustomWaveform(det_values_pulser)

        pulse = PulserPulse(amp_wf, det_wf, 0.0)

        pulser_sequence.add(pulse, "ising")

        return pulser_sequence
