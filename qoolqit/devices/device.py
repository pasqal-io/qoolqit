from __future__ import annotations

from math import pi
from typing import Callable, Optional

import pulser
from pulser.backend.remote import RemoteConnection
from pulser.devices._device_datacls import BaseDevice

from .unit_converter import UnitConverter

UPPER_DURATION = 6000
UPPER_AMP = 4.0 * pi
UPPER_DET = 4.0 * pi
LOWER_DISTANCE = 5.0


class Device:
    """
    QoolQit Device wrapper around a Pulser BaseDevice.

    Attributes:
    - pulser_device (BaseDevice): a `BaseDevice` to build the QoolQit device from.
    - default_converter (Optional[UnitConverter]): optional unit converter to handle
        unit conversion. Defaults to the unit converter that rescales energies by the
        maximum allowed amplitude by the device.
    """

    def __init__(
        self,
        pulser_device: BaseDevice,
        default_converter: Optional[UnitConverter] = None,
    ) -> None:

        if not isinstance(pulser_device, BaseDevice):
            raise TypeError("`pulser_device` must be an instance of Pulser BaseDevice class.")

        # Store it for all subsequent lookups
        self._pulser_device: BaseDevice = pulser_device
        self._name: str = self._pulser_device.name

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

    @property
    def _device(self) -> BaseDevice:
        """Pulser device used by this QoolQit Device."""
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
        return self._name

    def __repr__(self) -> str:
        return self._name


class MockDevice(Device):
    """A virtual device for unconstrained prototyping."""

    def __init__(self) -> None:
        super().__init__(pulser_device=pulser.MockDevice)


class AnalogDevice(Device):
    """A realistic device for analog sequence execution."""

    def __init__(self) -> None:
        super().__init__(pulser_device=pulser.AnalogDevice)


class DigitalAnalogDevice(Device):
    """A device with digital and analog capabilities."""

    def __init__(self) -> None:
        super().__init__(pulser_device=pulser.DigitalAnalogDevice)


class RemoteDevice(Device):
    """QoolQit device from remotely available pulser device."""
    def __init__(self, connection: RemoteConnection, name: str) -> None:
        if not isinstance(connection, RemoteConnection):
            raise TypeError("connection must be of type `RemoteConnection`.")
        available_devices = connection.fetch_available_devices()
        if name not in available_devices:
            available_device_names = list(available_devices.keys())
            raise ValueError(
                f"device {name} is not in the available devices of the provided connection: "
                f"{available_device_names}"
            )
        pulser_remote_device = connection.fetch_available_devices()[name]
        super().__init__(pulser_device=pulser_remote_device)
