from __future__ import annotations

from abc import ABC, abstractmethod
from math import pi

from pulser.devices._device_datacls import BaseDevice

from ._pulser_devices import _AnalogDevice, _MockDevice, _TestAnalogDevice
from .unit_converter import UnitConverter

UPPER_DURATION = 6000
UPPER_AMP = 4.0 * pi
UPPER_DET = 4.0 * pi
LOWER_DISTANCE = 5.0


class Device(ABC):
    """Abstract base class for a Device in QoolQit.

    The device in QoolQit holds a Pulser device, and all the logic is based on that.
    Defining a new device for usage in QoolQit should be done by inheriting from this base
    class and overriding the `_device` private property with the corresponding Pulser device.
    """

    def __init__(self) -> None:

        self._C6 = self._device.interaction_coeff
        self._clock_period = self._device.channels["rydberg_global"].clock_period

        # Relevant limits from the underlying device (float or None)
        self._max_duration = self._device.max_sequence_duration
        self._max_amp = self._device.channels["rydberg_global"].max_amp
        self._max_det = self._device.channels["rydberg_global"].max_abs_detuning
        self._min_distance = self._device.min_atom_distance

        # Values to use when limits do not exist
        self._upper_duration = self._max_duration or UPPER_DURATION
        self._upper_amp = self._max_amp or UPPER_AMP
        self._upper_det = self._max_det or UPPER_DET
        self._lower_distance = self._min_distance or LOWER_DISTANCE

        self.reset_converter()

    @property
    @abstractmethod
    def _device(self) -> BaseDevice:
        """Abstract property defining the Pulser device."""
        ...

    @property
    @abstractmethod
    def _default_converter(self) -> UnitConverter:
        """Abstract property defining the default unit converter."""
        ...

    @property
    def specs(self) -> dict:
        TIME, ENERGY, DISTANCE = self.converter.factors
        return {
            "max_duration": self._max_duration / TIME if self._max_duration else None,
            "max_amplitude": self._max_amp / ENERGY if self._max_amp else None,
            "max_detuning": self._max_det / ENERGY if self._max_det else None,
            "min_distance": self._min_distance / DISTANCE if self._min_distance else None,
        }

    @property
    def name(self) -> str:
        name: str = self._device.name
        return name

    def __post_init__(self) -> None:
        if not isinstance(self._device, BaseDevice):
            raise TypeError("Incorrect base device set.")

    def __repr__(self) -> str:
        return self.name

    @property
    def converter(self) -> UnitConverter:
        return self._converter

    def reset_converter(self) -> None:
        """Resets the unit converter to the default one."""
        self._converter = self._default_converter

    def set_time_unit(self, time: float) -> None:
        """Changes the unit converter according to a reference time unit."""
        self.converter.factors = self.converter.factors_from_time(time)

    def set_energy_unit(self, energy: float) -> None:
        """Changes the unit converter according to a reference energy unit."""
        self.converter.factors = self.converter.factors_from_energy(energy)

    def set_distance_unit(self, distance: float) -> None:
        """Changes the unit converter according to a reference distance unit."""
        self.converter.factors = self.converter.factors_from_distance(distance)


class MockDevice(Device):
    """An ideal device without constraints."""

    @property
    def _device(self) -> BaseDevice:
        return _MockDevice

    @property
    def _default_converter(self) -> UnitConverter:
        return UnitConverter.from_energy(self._C6, self._upper_amp)


class AnalogDevice(Device):
    """A realistic device with constraints mimicking a real QPU."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def _device(self) -> BaseDevice:
        return _AnalogDevice

    @property
    def _default_converter(self) -> UnitConverter:
        return UnitConverter.from_energy(self._C6, self._upper_amp)


class TestAnalogDevice(Device):
    """A realistic device with constraints mimicking a real QPU."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def _device(self) -> BaseDevice:
        return _TestAnalogDevice

    @property
    def _default_converter(self) -> UnitConverter:
        return UnitConverter.from_energy(self._C6, self._upper_amp)


ALL_DEVICES = [MockDevice, AnalogDevice, TestAnalogDevice]
