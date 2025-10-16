from __future__ import annotations

from math import pi
from typing import Callable, Optional, cast

from pulser.devices._device_datacls import BaseDevice

from ._pulser_devices import _AnalogDevice, _DigitalAnalogDevice, _MockDevice, _TestAnalogDevice
from .unit_converter import UnitConverter

UPPER_DURATION = 6000
UPPER_AMP = 4.0 * pi
UPPER_DET = 4.0 * pi
LOWER_DISTANCE = 5.0


class Device:
    """
    QoolQit Device wrapper around a Pulser BaseDevice.

    You can either:
      1) Instantiate directly with a Pulser device instance via `pulser_device=...`, or
      2) Subclass and override the `_device` property (backward-compatible path).
    """

    def __init__(
        self,
        pulser_device: Optional[BaseDevice] = None,
        default_converter: Optional[UnitConverter] = None,
    ) -> None:
        # Determine which Pulser device to use.
        if pulser_device is None:
            # If a subclass overrides `_device`, use that; otherwise error out.
            uses_override = type(self)._device is not Device._device
            if not uses_override:
                raise TypeError(
                    "Device requires `pulser_device` unless a subclass overrides `_device`."
                )
            # Access the subclass-provided device
            pulser_device = type(self)._device.__get__(self, type(self))

        if not isinstance(pulser_device, BaseDevice):
            raise TypeError("`pulser_device` must be an instance of Pulser BaseDevice class.")

        # Store it for all subsequent lookups
        self._pulser_device: BaseDevice = pulser_device

        # Physical constants / channel & limit lookups (assumes 'rydberg_global' channel)
        self._C6 = self._pulser_device.interaction_coeff
        self._clock_period = self._pulser_device.channels["rydberg_global"].clock_period
        # Relevant limits from the underlying device (float or None)
        self._max_duration = self._pulser_device.max_sequence_duration
        self._max_amp = self._pulser_device.channels["rydberg_global"].max_amp
        self._max_det = self._pulser_device.channels["rydberg_global"].max_abs_detuning
        self._min_distance = self._pulser_device.min_atom_distance

        # layouts
        self._requires_layout = self._pulser_device.requires_layout

        # Values to use when limits do not exist
        self._upper_duration = self._max_duration or UPPER_DURATION
        self._upper_amp = self._max_amp or UPPER_AMP
        self._upper_det = self._max_det or UPPER_DET
        self._lower_distance = self._min_distance or LOWER_DISTANCE

        if default_converter is not None:
            # Snapshot the caller-provided factors so reset() reproduces them exactly.
            t0, e0, d0 = default_converter.factors
            self._default_factory: Callable[[], UnitConverter] = lambda: UnitConverter(
                self._C6, t0, e0, d0
            )
        else:
            # Default from energy using C6 and the "upper" amplitude.
            self._default_factory = lambda: UnitConverter.from_energy(self._C6, self._upper_amp)

        self.reset_converter()
        self.__post_init__()

    @property
    def _device(self) -> BaseDevice:
        """Pulser device used by this QoolQit Device.

        Subclasses may override this property to provide a default device.
        """
        # Base implementation returns the explicitly provided device.
        return self._pulser_device

    @property
    def _default_converter(self) -> UnitConverter:
        """Default unit converter for this device (fresh instance each call)."""
        return self._default_factory()

    @property
    def converter(self) -> UnitConverter:
        return self._converter

    def reset_converter(self) -> None:
        """Resets the unit converter to the default one."""
        # Create a NEW converter so mutations don't persist.
        self._converter = self._default_converter

    # Unit setters mirror the original behavior
    def set_time_unit(self, time: float) -> None:
        """Changes the unit converter according to a reference time unit."""
        self.converter.factors = self.converter.factors_from_time(time)

    def set_energy_unit(self, energy: float) -> None:
        """Changes the unit converter according to a reference energy unit."""
        self.converter.factors = self.converter.factors_from_energy(energy)

    def set_distance_unit(self, distance: float) -> None:
        """Changes the unit converter according to a reference distance unit."""
        self.converter.factors = self.converter.factors_from_distance(distance)

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
        return cast(str, self._device.name)

    def __post_init__(self) -> None:
        if not isinstance(self._device, BaseDevice):
            raise TypeError("Incorrect base device set.")

    def __repr__(self) -> str:
        return self.name


class MockDevice(Device):
    def __init__(self) -> None:
        super().__init__(pulser_device=_MockDevice)


class AnalogDevice(Device):
    def __init__(self) -> None:
        super().__init__(pulser_device=_AnalogDevice)


class DigitalAnalogDevice(Device):
    """A device with digital and analog capabilites."""

    def __init__(self) -> None:
        super().__init__(pulser_device=_DigitalAnalogDevice)


class TestAnalogDevice(Device):
    def __init__(self) -> None:
        super().__init__(pulser_device=_TestAnalogDevice)


ALL_DEVICES = [MockDevice, AnalogDevice, TestAnalogDevice, DigitalAnalogDevice]
