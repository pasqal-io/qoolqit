from __future__ import annotations

from dataclasses import dataclass, field
from math import isclose


def _factors_from_time(C6: float, time: float) -> tuple[float, ...]:
    energy = 1000.0 / time
    distance = (C6 / energy) ** (1 / 6)
    return time, energy, distance


def _factors_from_energy(C6: float, energy: float) -> tuple[float, ...]:
    time = 1000.0 / energy
    distance = (C6 / energy) ** (1 / 6)
    return time, energy, distance


def _factors_from_distance(C6: float, distance: float) -> tuple[float, ...]:
    energy = C6 / distance
    time = 1000.0 / energy
    return time, energy, distance


@dataclass
class UnitConverter:
    """
    A dataclass representing a unit converter in the Rydberg-Analog model.

    Includes three inter-dependent factors for TIME, ENERGY and DISTANCE conversion, also depending
    on the interaction coeffiecient C6. The converter checks the following invariants:

    Invariants:
    1. ENERGY = 1000 / TIME ( <=> TIME * ENERGY = 1000 )
    2. DISTANCE = (C6 / ENERGY) ^ (1/6) ( <=> DISTANCE^6 * ENERGY = C6 )
    """

    """Interaction coefficient."""
    C6: float = field(repr=False)
    """Time conversion factor."""
    time: float
    """Energy conversion factor."""
    energy: float
    """Distance conversion factor."""
    distance: float

    def __post_init__(self) -> None:
        time_energy_inv = self.time * self.energy
        energy_dist_inv = (self.distance**6) * self.energy

        if not isclose(time_energy_inv, 1000.0):
            raise ValueError("Invalid unit converter, time-energy invariant violated.")
        elif not isclose(energy_dist_inv, self.C6):
            raise ValueError("Invalid unit converter, energy-distance invariant violated.")

    @classmethod
    def from_time(cls, C6: float, time: float) -> UnitConverter:
        time, energy, distance = _factors_from_time(C6, time)
        return UnitConverter(C6, time, energy, distance)

    @classmethod
    def from_energy(cls, C6: float, energy: float) -> UnitConverter:
        time, energy, distance = _factors_from_energy(C6, energy)
        return UnitConverter(C6, time, energy, distance)

    @classmethod
    def from_distance(cls, C6: float, distance: float) -> UnitConverter:
        time, energy, distance = _factors_from_distance(C6, distance)
        return UnitConverter(C6, time, energy, distance)

    @property
    def factors(self) -> tuple[float, ...]:
        return self.time, self.energy, self.distance

    def set_time_unit(self, time: float) -> None:
        self.time, self.energy, self.distance = _factors_from_time(self.C6, time)

    def set_energy_unit(self, energy: float) -> None:
        self.time, self.energy, self.distance = _factors_from_energy(self.C6, energy)

    def set_distance_unit(self, distance: float) -> None:
        self.time, self.energy, self.distance = _factors_from_distance(self.C6, distance)
