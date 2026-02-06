from __future__ import annotations

import random
from typing import Callable

import numpy as np
import pytest
from pulser_pasqal import PasqalCloud

from qoolqit import AnalogDevice, Device, DigitalAnalogDevice, MockDevice
from qoolqit.devices.unit_converter import UnitConverter

QOOLQIT_DEFAULT_DEVICES = [AnalogDevice, DigitalAnalogDevice, MockDevice]


def _validate_invariants(c6: float, t: float, e: float, d: float) -> np.bool:
    # Verify time-energy and energy-interaction invariants
    return np.isclose(t * e, 1000) and np.isclose(e * (d**6), c6)


def test_device_pulser_device_type() -> None:
    with pytest.raises(
        TypeError, match="`pulser_device` must be an instance of Pulser BaseDevice class."
    ):
        Device(pulser_device="device")  # type: ignore


def test_unit_converter() -> None:
    # Some arbitrary value for the interaction coefficient
    # that would come from a real device.
    C6 = 5000.0 * random.random()

    with pytest.raises(ValueError):
        converter = UnitConverter(C6, random.random(), random.random(), random.random())

    converter = UnitConverter.from_time(C6, 10.0 * random.random())
    assert _validate_invariants(C6, *converter.factors)

    converter = UnitConverter.from_energy(C6, 10.0 * random.random())
    assert _validate_invariants(C6, *converter.factors)

    converter = UnitConverter.from_distance(C6, 10.0 * random.random())
    assert _validate_invariants(C6, *converter.factors)

    converter.factors = converter.factors_from_time(10.0 * random.random())
    converter.factors = converter.factors_from_energy(10.0 * random.random())
    converter.factors = converter.factors_from_distance(10.0 * random.random())

    with pytest.raises(ValueError):
        # Wrong number of factors provided
        converter.factors = (random.random(), random.random())

    with pytest.raises(ValueError):
        # Factors that violate the invariants
        converter.factors = (random.random(), random.random(), random.random())


@pytest.mark.parametrize("device_class", QOOLQIT_DEFAULT_DEVICES)
def test_device_init_and_units(device_class: Callable) -> None:
    device = device_class()

    TIME_ORIG, ENERGY_ORIG, DISTANCE_ORIG = device.converter.factors
    assert _validate_invariants(device._C6, *device.converter.factors)

    device.set_time_unit(10.0)
    assert _validate_invariants(device._C6, *device.converter.factors)

    device.set_energy_unit(10.0)
    assert _validate_invariants(device._C6, *device.converter.factors)

    device.set_distance_unit(10.0)
    assert _validate_invariants(device._C6, *device.converter.factors)

    device.reset_converter()
    TIME_NEW, ENERGY_NEW, DISTANCE_NEW = device.converter.factors
    assert TIME_ORIG == pytest.approx(TIME_NEW)
    assert ENERGY_ORIG == pytest.approx(ENERGY_NEW)
    assert DISTANCE_ORIG == pytest.approx(DISTANCE_NEW)


def test_default_device_specs() -> None:
    mock_device = MockDevice()
    expected_mock_specs = {
        "max_duration": None,
        "max_amplitude": None,
        "max_abs_detuning": None,
        "min_distance": None,
        "max_radial_distance": None,
    }
    assert mock_device.specs == expected_mock_specs
    assert mock_device.energy_ratio is None

    analog_device = AnalogDevice()
    expected_analog_specs = {
        "max_duration": 75.39822368615503,
        "max_amplitude": 1.0,
        "max_abs_detuning": 10.0,
        "min_distance": 0.7809234915702248,
        "max_radial_distance": 5.935018535933708,
    }
    assert analog_device.specs == expected_analog_specs
    assert analog_device.energy_ratio is not None
    assert analog_device.energy_ratio == 0.22680411206965717

    digital_analog_device = DigitalAnalogDevice()
    expected_digital_analog_specs = {
        "max_duration": None,
        "max_amplitude": 1.0,
        "max_abs_detuning": 8.0,
        "min_distance": 0.47761501632709613,
        "max_radial_distance": 5.970187704088701,
    }
    assert digital_analog_device.specs == expected_digital_analog_specs
    assert digital_analog_device.energy_ratio is not None
    assert digital_analog_device.energy_ratio == 0.011870467845064849


def test_device_from_connection() -> None:
    fresnel_device = Device.from_connection(PasqalCloud(), "FRESNEL")
    assert fresnel_device.name == "FRESNEL"

    expected_fresnel_specs = {
        "max_duration": 67.85840131753953,
        "max_amplitude": 1.0,
        "max_abs_detuning": 5.555555555555555,
        "min_distance": 0.7673301077365813,
        "max_radial_distance": 7.059436991176549,
    }

    assert fresnel_device.specs == expected_fresnel_specs
    assert fresnel_device.energy_ratio is not None
    assert fresnel_device.energy_ratio == 0.20412370086269147


def test_device_from_connection_not_available() -> None:
    with pytest.raises(
        ValueError, match="Device HELLO_WORLD is not available through the provided connection."
    ):
        Device.from_connection(connection=PasqalCloud(), name="HELLO_WORLD")
