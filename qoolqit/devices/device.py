from __future__ import annotations

from dataclasses import InitVar, asdict, dataclass

from pulser.devices import AnalogDevice as _AnalogDevice
from pulser.devices import MockDevice as _MockDevice
from pulser.devices._device_datacls import BaseDevice


@dataclass
class Device:

    device: InitVar[BaseDevice]
    name: str | None = None
    max_n_qubits: int | None = None
    min_qubit_distance: float | None = None
    max_sequence_duration: int | None = None

    def __post_init__(self, device: BaseDevice) -> None:
        self._device = device
        self.name: str = self._device.name
        self.max_n_qubits: int | None = self._device.max_atom_num
        self.min_qubit_distance: float = self._device.min_atom_distance
        self.max_sequence_duration: int | None = self._device.max_sequence_duration

        self._c6 = device.interaction_coeff
        self._max_amp = device.channels["rydberg_global"].max_amp
        self._max_det = device.channels["rydberg_global"].max_abs_detuning

    def __repr__(self) -> str:
        return self.name  # type: ignore [return-value]

    @property
    def specs_dict(self) -> dict:
        """Device specifications."""
        return asdict(self)


MockDevice = Device(_MockDevice)
AnalogDevice = Device(_AnalogDevice)
