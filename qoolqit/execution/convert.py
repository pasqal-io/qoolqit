from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from math import pi

from qoolqit.devices import Device


@dataclass
class UnitConverter:
    """Device to target."""

    device: InitVar[Device]
    """Time conversion factor."""
    time: float = field(init=False)
    """Energy conversion factor."""
    energy: float = field(init=False)
    """Distance conversion factor."""
    distance: float = field(init=False)

    @property
    def factors(self) -> tuple[float, ...]:
        return self.time, self.energy, self.distance

    def __post_init__(self, device: Device) -> None:
        self._device = device
        self._c6 = self._device._c6

        # For now we just default to setting the reference energy
        energy = self._device._max_amp or 4.0 * pi
        self.set_energy_unit(energy)

    def set_energy_unit(self, energy: float) -> None:
        self.energy = energy
        self.time = 1000.0 / self.energy
        self.distance = (self._c6 / self.energy) ** (1 / 6)

    def set_distance_unit(self, distance: float) -> None:
        self.distance = distance
        self.energy = self._c6 / (self.distance**6)
        self.time = 1000.0 / self.energy
