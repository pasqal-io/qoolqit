from __future__ import annotations

from pulser import CustomWaveform as PulserCustomWaveform
from pulser import Pulse as PulserPulse
from pulser import Register as PulserRegister
from pulser import Sequence as PulserSequence

from qoolqit.devices import Device, UnitConverter
from qoolqit.register import Register
from qoolqit.sequence import Sequence

__all__ = ["QuantumProgram"]


class QuantumProgram:
    def __init__(
        self,
        register: Register,
        sequence: Sequence,
    ) -> None:

        self._register = register
        self._sequence = sequence
        self._compiled_sequence: Sequence | None = None

    @property
    def register(self) -> Register:
        return self._register

    @property
    def sequence(self) -> Sequence:
        return self._sequence

    @property
    def compiled_sequence(self) -> PulserSequence:
        if self._compiled_sequence is None:
            raise ValueError(
                "Program has not been compiled. Please call program.compile_to(device)."
            )
        else:
            return self._compiled_sequence

    def compile_to(self, device: Device) -> None:

        # Draft logic, to see how to best organize it...

        converter = UnitConverter(device)

        converted_duration = self.sequence.duration * converter.time

        time_array_pulser = list(range(int(converted_duration) + 1))

        time_array_qoolqit = [t / converter.time for t in time_array_pulser]

        amp_values_qoolqit = self.sequence.amplitude(time_array_qoolqit)
        det_values_qoolqit = self.sequence.detuning(time_array_qoolqit)

        amp_values_pulser = [amp * converter.energy for amp in amp_values_qoolqit]
        det_values_pulser = [det * converter.energy for det in det_values_qoolqit]

        coords_qoolqit = self.register.qubits
        coords_pulser = {q: converter.distance * c for q, c in coords_qoolqit.items()}

        pulser_device = device._device
        pulser_register = PulserRegister(coords_pulser)
        pulser_sequence = PulserSequence(pulser_register, pulser_device)
        pulser_sequence.declare_channel("ising", "rydberg_global")

        amp_wf = PulserCustomWaveform(amp_values_pulser)
        det_wf = PulserCustomWaveform(det_values_pulser)

        pulse = PulserPulse(amp_wf, det_wf, 0.0)

        pulser_sequence.add(pulse, "ising")

        self._compiled_sequence = pulser_sequence
