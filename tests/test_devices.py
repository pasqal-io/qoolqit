from __future__ import annotations

import random

import numpy as np
import pytest
from pulser_pasqal import PasqalCloud

from qoolqit import AnalogDevice, Device, DigitalAnalogDevice, MockDevice
from qoolqit.devices.unit_converter import UnitConverter


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


@pytest.mark.parametrize("device", [AnalogDevice(), DigitalAnalogDevice(), MockDevice()])
def test_device_init_and_units(device: Device) -> None:

    TIME_ORIG, ENERGY_ORIG, DISTANCE_ORIG = device.converter.factors
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
        "min_distance": 0,
        "max_radial_distance": None,
    }
    assert mock_device.specs == expected_mock_specs

    analog_device = AnalogDevice()
    expected_analog_specs = {
        "max_duration": 332.43763968,
        "max_amplitude": 0.22680411206965717,
        "max_abs_detuning": 2.268041120696572,
        "min_distance": 1.0,
        "max_radial_distance": 7.6,
    }
    assert analog_device.specs == expected_analog_specs

    digital_analog_device = DigitalAnalogDevice()
    expected_digital_analog_specs = {
        "max_duration": None,
        "max_amplitude": 0.011870467845064849,
        "max_abs_detuning": 0.09496374276051879,
        "min_distance": 1.0,
        "max_radial_distance": 12.5,
    }
    assert digital_analog_device.specs == expected_digital_analog_specs


def test_device_properties() -> None:
    mock_device = MockDevice()
    assert mock_device.name == "MockDevice"
    # default value for reference only
    assert mock_device._energy_ratio == 0.03622579298420669
    np.testing.assert_allclose(mock_device._upper_amp, 4 * np.pi)
    np.testing.assert_allclose(mock_device._target_amp, 4 * np.pi)
    np.testing.assert_allclose(mock_device._target_amp_adim, 0.03622579298420669)
    np.testing.assert_allclose(mock_device._upper_amp, 4 * np.pi)
    assert mock_device._lower_distance == 5.0
    np.testing.assert_allclose(mock_device._target_dist, 5.0)
    np.testing.assert_allclose(mock_device._target_dist_adim, 1.0)

    analog_device = AnalogDevice()
    assert analog_device.name == "AnalogDevice"
    assert analog_device._energy_ratio == 0.22680411206965717
    np.testing.assert_allclose(analog_device._upper_amp, 4 * np.pi)
    np.testing.assert_allclose(analog_device._target_amp, 4 * np.pi)
    np.testing.assert_allclose(analog_device._target_amp_adim, 0.22680411206965717)
    np.testing.assert_allclose(analog_device._upper_amp, 4 * np.pi)
    assert analog_device._lower_distance == 5.0
    np.testing.assert_allclose(analog_device._target_dist, 5.0)
    np.testing.assert_allclose(analog_device._target_dist_adim, 1.0)

    digital_analog_device = DigitalAnalogDevice()
    assert digital_analog_device.name == "DigitalAnalogDevice"
    assert digital_analog_device._energy_ratio == 0.011870467845064849
    np.testing.assert_allclose(digital_analog_device._upper_amp, 5 * np.pi)
    np.testing.assert_allclose(digital_analog_device._target_amp, 5 * np.pi)
    np.testing.assert_allclose(digital_analog_device._target_amp_adim, 0.011870467845064849)
    np.testing.assert_allclose(digital_analog_device._upper_amp, 5 * np.pi)
    assert digital_analog_device._lower_distance == 4.0
    np.testing.assert_allclose(digital_analog_device._target_dist, 4.0)
    np.testing.assert_allclose(digital_analog_device._target_dist_adim, 1.0)


def test_device_from_connection() -> None:
    fresnel_device = Device.from_connection(PasqalCloud(), "FRESNEL")
    assert fresnel_device.name == "FRESNEL"

    expected_fresnel_specs = {
        "max_duration": 332.43763968,
        "max_amplitude": 0.20412370086269147,
        "max_abs_detuning": 1.134020560348286,
        "min_distance": 1.0,
        "max_radial_distance": 9.2,
    }

    assert fresnel_device.specs == expected_fresnel_specs
    assert fresnel_device._energy_ratio == 0.20412370086269147


def test_device_from_connection_not_available() -> None:
    with pytest.raises(
        ValueError, match="Device HELLO_WORLD is not available through the provided connection."
    ):
        Device.from_connection(connection=PasqalCloud(), name="HELLO_WORLD")
