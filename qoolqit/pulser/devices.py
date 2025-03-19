from __future__ import annotations

from dataclasses import dataclass

from pulser.devices import AnalogDevice as _AnalogDevice
from pulser.devices import MockDevice as _MockDevice
from pulser.devices._device_datacls import BaseDevice


@dataclass
class Device:

    _device: BaseDevice

    def __post_init__(self) -> None:
        self.name: str = self._device.name
        self.max_n_qubits: int | None = self._device.max_atom_num

    def __repr__(self) -> str:
        return self.name


MockDevice = Device(_MockDevice)
AnalogDevice = Device(_AnalogDevice)
