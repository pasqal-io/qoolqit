from __future__ import annotations

from dataclasses import InitVar, dataclass
from math import pi

from .device import Device

__all__ = ["UnitConverter"]

"""
At the end we need to have something like.

converter.time
converter.energy
converter.distance
"""


@dataclass
class UnitConverter:
    """Device to target."""

    device: InitVar[Device]
    """Time conversion factor."""
    time: float | None = None
    """Energy conversion factor."""
    energy: float | None = None
    """Distance conversion factor."""
    distance: float | None = None

    def __post_init__(self, device: Device) -> None:

        self._device = device

        self.energy = self._device._max_amp or 4.0 * pi
        self.time = 1000.0 / self.energy
        self.distance = (self._device._c6 / self.energy) ** (1 / 6)
