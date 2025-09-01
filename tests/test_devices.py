from __future__ import annotations

import random
from typing import Callable

import pytest

from qoolqit.devices import (
    ALL_DEVICES,
    AvailableDevices,
    UnitConverter,
)
from qoolqit.utils import ATOL_32, EQUAL


def _validate_invariants(c6: float, t: float, e: float, d: float) -> bool:
    # Verify time-energy and energy-distance invariants
    return EQUAL(t * e, 1.0, atol=ATOL_32) and EQUAL(e * (d**6), c6, atol=ATOL_32)


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


@pytest.mark.parametrize("device_class", ALL_DEVICES)
def test_device_init_and_units(device_class: Callable) -> None:
    device = device_class()
    assert device.name in AvailableDevices.list(values=True)

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
    assert EQUAL(TIME_ORIG, TIME_NEW)
    assert EQUAL(ENERGY_ORIG, ENERGY_NEW)
    assert EQUAL(DISTANCE_ORIG, DISTANCE_NEW)
