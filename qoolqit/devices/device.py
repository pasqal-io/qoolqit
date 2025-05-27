from __future__ import annotations

from dataclasses import InitVar, asdict, dataclass, field
from math import pi

from pulser.devices import AnalogDevice as _AnalogDevice
from pulser.devices import MockDevice as _MockDevice
from pulser.devices._device_datacls import BaseDevice

from .unit_converter import UnitConverter

DEFAULT_TIME = 80.0
DEFAULT_ENERGY = 4.0 * pi
DEFAULT_DISTANCE = 8.0


@dataclass
class Device:

    device: InitVar[BaseDevice]
    name: str = field(init=False)
    max_n_qubits: int = field(init=False)

    _converter: UnitConverter = field(init=False)

    # min_qubit_distance: float = field(init=False)
    # max_sequence_duration: int = field(init=False)

    def __post_init__(self, device: BaseDevice) -> None:
        self._device = device
        self.name: str = self._device.name
        self.max_n_qubits: int | None = self._device.max_atom_num

        # self.min_qubit_distance: float = self._device.min_atom_distance
        # self.max_sequence_duration: int | None = self._device.max_sequence_duration

        self._C6 = device.interaction_coeff
        self._max_amp = device.channels["rydberg_global"].max_amp
        self._max_det = device.channels["rydberg_global"].max_abs_detuning
        self._max_duration = device.max_sequence_duration

        self._converter = UnitConverter.from_energy(self._C6, self._max_amp or DEFAULT_ENERGY)

    def __repr__(self) -> str:
        return self.name

    @property
    def unit_converter(self) -> UnitConverter:
        return self._converter

    @property
    def specs_dict(self) -> dict:
        """Device specifications."""
        return asdict(self)


# FIXME: THIS DOES NOT WORK
# Mutability is a problem
MockDevice = Device(_MockDevice)
AnalogDevice = Device(_AnalogDevice)
