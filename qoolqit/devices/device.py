from __future__ import annotations

from abc import ABC, abstractmethod
from math import pi

from pulser.devices import AnalogDevice as _AnalogDevice
from pulser.devices import MockDevice as _MockDevice
from pulser.devices._device_datacls import BaseDevice

from .unit_converter import UnitConverter

UPPER_DURATION = 6000
UPPER_AMP = 4.0 * pi
UPPER_DET = 4.0 * pi


class Device(ABC):

    def __init__(self) -> None:

        self._C6 = self._device.interaction_coeff
        self._max_duration = self._device.max_sequence_duration or UPPER_DURATION
        self._max_amp = self._device.channels["rydberg_global"].max_amp or UPPER_AMP
        self._max_det = self._device.channels["rydberg_global"].max_abs_detuning or UPPER_DET

        self.set_default_converter()

    @property
    @abstractmethod
    def _device(self) -> BaseDevice:
        """Abstract property setting the Pulser device."""
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

    def set_default_converter(self) -> None:
        self._converter = UnitConverter.from_energy(self._C6, self._max_amp)

    def set_time_unit(self, time: float) -> None:
        self.converter.set_time_unit(time)

    def set_energy_unit(self, energy: float) -> None:
        self.converter.set_energy_unit(energy)

    def set_distance_unit(self, distance: float) -> None:
        self.converter.set_distance_unit(distance)


class MockDevice(Device):
    @property
    def _device(self) -> BaseDevice:
        return _MockDevice


class AnalogDevice(Device):
    @property
    def _device(self) -> BaseDevice:
        return _AnalogDevice
