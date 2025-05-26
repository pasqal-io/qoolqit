from __future__ import annotations

from typing import Callable

from pulser import Sequence as PulserSequence

from qoolqit.devices import Device, UnitConverter
from qoolqit.register import Register
from qoolqit.sequence import Sequence

from .compilation_functions import compile_to_analog_device, compile_to_mock_device

COMPILATION_FUNCTIONS = {
    "MockDevice": compile_to_mock_device,
    "AnalogDevice": compile_to_analog_device,
}


class SequenceCompiler:
    def __init__(self, register: Register, sequence: Sequence, device: Device):

        self._register = register
        self._sequence = sequence
        self._device = device

        self._target_device = device._device
        self._converter = UnitConverter(device)

        self._compilation_function: Callable | None = COMPILATION_FUNCTIONS.get(device.name, None)

    @property
    def register(self) -> Register:
        return self._register

    @property
    def sequence(self) -> Sequence:
        return self._sequence

    @property
    def device(self) -> Device:
        return self._device

    @property
    def converter(self) -> UnitConverter:
        return self._converter

    def set_energy_unit(self, energy: float) -> None:
        self._converter.set_energy_unit(energy)

    def set_distance_unit(self, energy: float) -> None:
        self._converter.set_distance_unit(energy)

    def compile_sequence(self) -> PulserSequence:
        if self._compilation_function is None:
            raise ValueError(f"Device {self.device.name} has an unknown compilation function.")
        else:
            return self._compilation_function(self.register, self.sequence, self.converter)
