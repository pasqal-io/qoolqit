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
    on the interaction coeffiecient C6. The converter checks the following invariants, based on the
    units used by Pulser:

    Invariants:
    1. TIME * ENERGY = 1000 ( <=> TIME = 1000 / ENERGY )
    2. DISTANCE^6 * ENERGY = C6 ( <=> ENERGY = C6 / (DISTANCE ^ 6) )
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
        self._validate_factors(self.time, self.energy, self.distance)

    def _validate_factors(self, time: float, energy: float, distance: float) -> None:
        time_energy_inv = time * energy
        energy_dist_inv = (distance**6) * energy

        if not isclose(time_energy_inv, 1000.0):
            raise ValueError("Invalid set of factors, time-energy invariant violated.")
        elif not isclose(energy_dist_inv, self.C6):
            raise ValueError("Invalid set of factors, energy-distance invariant violated.")

    @classmethod
    def from_time(cls, C6: float, time: float) -> UnitConverter:
        """Instantiate from a reference C6 value and a reference time unit."""
        time, energy, distance = _factors_from_time(C6, time)
        return UnitConverter(C6, time, energy, distance)

    @classmethod
    def from_energy(cls, C6: float, energy: float) -> UnitConverter:
        """Instantiate from a reference C6 value and a reference energy unit."""
        time, energy, distance = _factors_from_energy(C6, energy)
        return UnitConverter(C6, time, energy, distance)

    @classmethod
    def from_distance(cls, C6: float, distance: float) -> UnitConverter:
        """Instantiate from a reference C6 value and a reference distance unit."""
        time, energy, distance = _factors_from_distance(C6, distance)
        return UnitConverter(C6, time, energy, distance)

    @property
    def factors(self) -> tuple[float, ...]:
        """Return the current conversion factors set."""
        return self.time, self.energy, self.distance

    @factors.setter
    def factors(self, values: tuple[float, ...]) -> None:
        """Set the conversion factors to new ones."""
        if (not isinstance(values, tuple)) or len(values) != 3:
            raise ValueError(
                "Setting the conversion factors requires 3 values passed "
                "as a tuple `(time, energy, distance)`."
            )
        self._validate_factors(*values)
        self.time = values[0]
        self.energy = values[1]
        self.distance = values[2]

    def factors_from_time(self, time: float) -> tuple[float, ...]:
        """Factors from a different reference time than the one set."""
        return _factors_from_time(self.C6, time)

    def factors_from_energy(self, energy: float) -> tuple[float, ...]:
        """Factors from a different reference energy than the one set."""
        return _factors_from_energy(self.C6, energy)

    def factors_from_distance(self, distance: float) -> tuple[float, ...]:
        """Factors from a different reference energy than the one set."""
        return _factors_from_distance(self.C6, distance)

    # def set_time_unit(self, time: float) -> None:
    #     """Set factors from a new reference time unit."""
    #     self.time, self.energy, self.distance = self.factors_from_time(time)

    # def set_energy_unit(self, energy: float) -> None:
    #     self.time, self.energy, self.distance = self.factors_from_energy(energy)

    # def set_distance_unit(self, distance: float) -> None:
    #     self.time, self.energy, self.distance = self.factors_from_distance(distance)
