from __future__ import annotations

import pytest
import math
import random

from qoolqit.devices import (
    UnitConverter,
)


def test_unit_converter() -> None:

    # Some arbitrary value for the interaction coefficient
    # that would come from a real device.
    C6 = 5000.0 * random.random()

    with pytest.raises(ValueError):
        converter = UnitConverter(C6, random.random(), random.random(), random.random())
    
    converter = UnitConverter.from_time(C6, 10.0 * random.random())
    TIME, ENERGY, DISTANCE = converter.factors
    assert math.isclose(TIME * ENERGY, 1000.0)  # time-energy invariant
    assert math.isclose(ENERGY * (DISTANCE ** 6), C6)  # energy-distance invariant

    converter = UnitConverter.from_energy(C6, 10.0 * random.random())
    TIME, ENERGY, DISTANCE = converter.factors
    assert math.isclose(TIME * ENERGY, 1000.0)  # time-energy invariant
    assert math.isclose(ENERGY * (DISTANCE ** 6), C6)  # energy-distance invariant

    converter = UnitConverter.from_distance(C6, 10.0 * random.random())
    TIME, ENERGY, DISTANCE = converter.factors
    assert math.isclose(TIME * ENERGY, 1000.0)  # time-energy invariant
    assert math.isclose(ENERGY * (DISTANCE ** 6), C6)  # energy-distance invariant

    converter.factors = converter.factors_from_time(10.0 * random.random())
    converter.factors = converter.factors_from_energy(10.0 * random.random())
    converter.factors = converter.factors_from_distance(10.0 * random.random())

    with pytest.raises(ValueError):
        # Wrong number of factors provided
        converter.factors = (random.random(), random.random())

    with pytest.raises(ValueError):
        # Factors that violate the invariants
        converter.factors = (random.random(), random.random(), random.random())