from __future__ import annotations

from math import pi
from typing import Callable, Optional

import pulser
from pulser.backend.remote import RemoteConnection
from pulser.devices._device_datacls import BaseDevice

from .unit_converter import UnitConverter


class Device:
    """
    QoolQit Device wrapper around a Pulser BaseDevice.

    Args:
        pulser_device (BaseDevice): a `BaseDevice` to build the QoolQit device from.
        default_converter (Optional[UnitConverter]): optional unit converter to handle
            unit conversion. Defaults to the unit converter that rescales energies by the
            maximum allowed amplitude by the device.

    Examples:
        From Pulser device:
        ```python
        qoolqit_device = Device(pulser_device=pulser_device)
        ```

        From remote Pulser device:
        ```python
        from pulser_pasqal import PasqalCloud
        from qoolqit import Device

        # Fetch the remote device from the connection
        connection = PasqalCloud()
        pulser_fresnel_device = connection.fetch_available_devices()["FRESNEL"]

        # Wrap a Pulser device object into a QoolQit Device
        fresnel_device = Device(pulser_device=PulserFresnelDevice)
        ```

        From custom Pulser device:
        ```
        from dataclasses import replace
        from pulser import AnalogDevice
        from qoolqit import Device

        # Converting the pulser Device object in a VirtualDevice object
        VirtualAnalog = AnalogDevice.to_virtual()
        # Replacing desired values
        ModdedAnalogDevice = replace(
            VirtualAnalog,
            max_radial_distance=100,
            max_sequence_duration=7000
            )

        # Wrap a Pulser device object into a QoolQit Device
        mod_analog_device = Device(pulser_device=ModdedAnalogDevice)
        ```
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
        self._max_abs_det = self._pulser_device.channels["rydberg_global"].max_abs_detuning
        self._min_distance = self._pulser_device.min_atom_distance
        self._max_radial_distance = self._pulser_device.max_radial_distance

        # ratio between maximum amplitude and maximum interaction energy J_max = C6/r_min^6
        self._energy_ratio = None
        if self._max_amp and self._min_distance:
            self._energy_ratio = (self._max_amp * self._min_distance**6) / self._C6

        # layouts
        self._requires_layout = self._pulser_device.requires_layout

        if default_converter is not None:
            # Snapshot the caller-provided factors so reset() reproduces them exactly.
            t0, e0, d0 = default_converter.factors
            self._default_factory: Callable[[], UnitConverter] = lambda: UnitConverter(
                self._C6, t0, e0, d0
            )
        else:
            # Default from energy using C6 and max amplitude.
            # On MockDevice there is no max_amp so the reasonable reference is 4.0 * pi
            self._default_factory = lambda: UnitConverter.from_energy(
                self._C6, self._max_amp or 4.0 * pi
            )

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
    def specs(self) -> dict[str, float | None]:
        """Return the device specification constrains."""
        TIME, ENERGY, DISTANCE = self.converter.factors
        max_duration = self._max_duration / TIME if self._max_duration else None
        max_amplitude = self._max_amp / ENERGY if self._max_amp else None
        max_abs_detuning = self._max_abs_det / ENERGY if self._max_abs_det else None
        min_distance = self._min_distance / DISTANCE if self._min_distance else None
        max_radial_distance = (
            self._max_radial_distance / DISTANCE if self._max_radial_distance else None
        )
        return {
            "max_duration": max_duration,
            "max_amplitude": max_amplitude,
            "max_abs_detuning": max_abs_detuning,
            "min_distance": min_distance,
            "max_radial_distance": max_radial_distance,
        }

    @property
    def energy_ratio(self) -> float | None:
        """Return the ratio between the max amplitude and max interaction energy on this device."""
        return self._energy_ratio

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name

    def __str__(self) -> str:
        output = f"{self.name}: {self._device.short_description}\n"
        for k, v in self.specs.items():
            output += f" └── {k}: {v}\n"
        return output

    def info(self) -> None:
        """Show the device short description and constrains."""
        print(self)

    @classmethod
    def from_connection(cls, connection: RemoteConnection, name: str) -> Device:
        """Return the specified device from the selected device from a connection.

        Available devices through the provided connection are can be seen with
        the `connection.fetch_available_devices()` method.

        Args:
            connection (RemoteConnection): connection object to fetch the available devices.
            name (str): The name of the desired device.

        Example:
        ```python
        fresnel_device = Device.from_connection(connection=PasqalCloud(), name="FRESNEL")
        ```
        """
        available_remote_devices = connection.fetch_available_devices()
        if name not in available_remote_devices:
            raise ValueError(f"Device {name} is not available through the provided connection.")
        pulser_device = available_remote_devices[name]
        return cls(pulser_device=pulser_device)


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


def available_default_devices() -> None:
    """Show the default available devices in QooQit."""
    for dev in (AnalogDevice(), DigitalAnalogDevice(), MockDevice()):
        dev.info()
