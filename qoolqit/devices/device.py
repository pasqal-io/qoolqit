from __future__ import annotations

from abc import ABC, abstractmethod
from math import pi

from pulser.devices._device_datacls import BaseDevice

from ._pulser_devices import _AnalogDevice, _MockDevice, _TestAnalogDevice
from .unit_converter import UnitConverter

UPPER_DURATION = 6000
UPPER_AMP = 4.0 * pi
UPPER_DET = 4.0 * pi


class Device(ABC):
    """Abstract base class for a Device in QoolQit.

    The device in QoolQit holds a Pulser device, and all the logic is based on that.
    Defining a new device for usage in QoolQit should be done by inheriting from this base
    class and overriding the `_device` private property with the corresponding Pulser device.
    """

    def __init__(self) -> None:

        self._C6 = self._device.interaction_coeff
        self._clock_period = self._device.channels["rydberg_global"].clock_period
        self._max_duration = self._device.max_sequence_duration or UPPER_DURATION
        self._max_amp = self._device.channels["rydberg_global"].max_amp or UPPER_AMP
        self._max_det = self._device.channels["rydberg_global"].max_abs_detuning or UPPER_DET

        self.reset_converter()

    @property
    @abstractmethod
    def _device(self) -> BaseDevice:
        """Abstract property defining the Pulser device."""
        pass

    @property
    @abstractmethod
    def _default_converter(self) -> UnitConverter:
        """Abstract property defining the default unit converter."""
        pass

    @property
    def name(self) -> str:
        name: str = self._device.name
        return name

    def __post_init__(self) -> None:
        if not isinstance(self._device, BaseDevice):
            raise TypeError("Incorrent base device set.")

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
        return UnitConverter.from_energy(self._C6, self._max_amp)


class AnalogDevice(Device):
    """A realistic device with constraints mimicking a real QPU."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def _device(self) -> BaseDevice:
        return _AnalogDevice

    @property
    def _default_converter(self) -> UnitConverter:
        return UnitConverter.from_energy(self._C6, self._max_amp)


class TestAnalogDevice(Device):
    """A realistic device with constraints mimicking a real QPU."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def _device(self) -> BaseDevice:
        return _TestAnalogDevice

    @property
    def _default_converter(self) -> UnitConverter:
        return UnitConverter.from_energy(self._C6, self._max_amp)


ALL_DEVICES = [MockDevice, AnalogDevice, TestAnalogDevice]
