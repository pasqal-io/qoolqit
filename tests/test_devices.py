from __future__ import annotations

import random
from typing import Callable

import numpy as np
import pytest

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
        Device(pulser_device="device")


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
        "max_detuning": None,
        "min_distance": None,
    }
    assert mock_device.specs == expected_mock_specs

    analog_device = AnalogDevice()
    expected_analog_specs = {
        "max_duration": 75.39822368615503,
        "max_amplitude": 1.0,
        "max_detuning": 10.0,
        "min_distance": 0.7809234915702248,
    }
    assert analog_device.specs == expected_analog_specs

    digital_analog_device = DigitalAnalogDevice()
    expected_digital_analog_specs = {
        "max_duration": None,
        "max_amplitude": 1.0,
        "max_detuning": 8.0,
        "min_distance": 0.47761501632709613,
    }
    assert digital_analog_device.specs == expected_digital_analog_specs
