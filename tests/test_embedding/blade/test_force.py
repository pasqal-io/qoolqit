from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import qmc

from qoolqit.embedding.algorithms.blade._force import (
    Force,
    configured_increasing_func,
    modulate_cursor,
)


def low_discrepancy_distrib(n: int, *, d: int = 1) -> np.ndarray:
    return qmc.Sobol(d=d, scramble=True).random(n).reshape(n, d)


@pytest.fixture(params=list(map(tuple, low_discrepancy_distrib(2**5, d=2))))
def stiffness_middle_value(request: pytest.FixtureRequest) -> tuple[float, float]:
    stiffness, middle_value = request.param
    return stiffness, middle_value


def test_configured_increasing_func_constraints(
    stiffness_middle_value: tuple[float, float],
) -> None:
    stiffness, middle_value = stiffness_middle_value

    lower_bound_eval = configured_increasing_func(0, middle_value=middle_value, stiffness=stiffness)
    np.testing.assert_allclose(lower_bound_eval, 0)
    assert lower_bound_eval >= 0

    np.testing.assert_allclose(
        configured_increasing_func(0.5, middle_value=middle_value, stiffness=stiffness),
        middle_value,
    )

    upper_bound_eval = configured_increasing_func(1, middle_value=middle_value, stiffness=stiffness)
    np.testing.assert_allclose(upper_bound_eval, 1)
    assert upper_bound_eval <= 1


def test_configured_increasing_func_increasing(stiffness_middle_value: tuple[float, float]) -> None:
    stiffness, middle_value = stiffness_middle_value

    points = low_discrepancy_distrib(2**4)

    y = configured_increasing_func(points, middle_value=middle_value, stiffness=stiffness)
    assert np.all(np.diff(y) > 0)


def test_modulate_cursor_constraints(stiffness_middle_value: tuple[float, float]) -> None:
    stiffness, middle_value = stiffness_middle_value
    center_value = middle_value / 2

    np.testing.assert_allclose(
        modulate_cursor(
            strong_cursor=0.5, weak_cursor=0.5, center_value=center_value, stiffness=stiffness
        ),
        center_value,
    )

    np.testing.assert_allclose(
        modulate_cursor(
            strong_cursor=np.array([0, 0, 1, 1]),
            weak_cursor=np.array([0, 1, 0, 1]),
            center_value=center_value,
            stiffness=stiffness,
        ),
        np.array([0, 0, 0, 1]),
    )

    coordinate = low_discrepancy_distrib(2**4)

    min_strong_cursor_eval = modulate_cursor(
        strong_cursor=0, weak_cursor=coordinate, center_value=center_value, stiffness=stiffness
    )
    np.testing.assert_allclose(min_strong_cursor_eval, 0)

    max_strong_cursor_eval = modulate_cursor(
        strong_cursor=1, weak_cursor=coordinate, center_value=center_value, stiffness=stiffness
    )
    np.testing.assert_allclose(max_strong_cursor_eval, 1)

    min_weak_cursor_eval = modulate_cursor(
        strong_cursor=coordinate, weak_cursor=0, center_value=center_value, stiffness=stiffness
    )
    np.testing.assert_allclose(min_weak_cursor_eval, 0)

    max_weak_cursor_eval = modulate_cursor(
        strong_cursor=coordinate, weak_cursor=1, center_value=center_value, stiffness=stiffness
    )
    np.testing.assert_allclose(max_weak_cursor_eval, coordinate)


def test_modulate_cursor_increasing(
    stiffness_middle_value: tuple[float, float],
) -> None:
    stiffness, middle_value = stiffness_middle_value
    center_value = middle_value / 2

    points = low_discrepancy_distrib(2**5, d=2)
    cursors = modulate_cursor(
        strong_cursor=points[:, 0],
        weak_cursor=points[:, 1],
        center_value=center_value,
        stiffness=stiffness,
    )

    points_diffs = points[np.newaxis, :, :] - points[:, np.newaxis, :]
    mask = (points_diffs[:, :, 0] > 0) & (points_diffs[:, :, 1] > 0)
    cursors_diffs = cursors[np.newaxis, :] - cursors[:, np.newaxis]
    assert np.all(cursors_diffs[mask] > 0)


def test_regulated_with_zero_cursor_returns_clone() -> None:
    weighted_vectors = np.array([[1.0, 0.0], [0.5, 0.0]])
    distances_to_walk = np.array([2.0, 1.0])
    force = Force(weighted_vectors=weighted_vectors, distances_to_walk=distances_to_walk)

    regulated_force = force.regulated(regulation_cursor=0)

    np.testing.assert_allclose(
        regulated_force.weighted_vectors,
        force.weighted_vectors,
    )
    np.testing.assert_allclose(
        regulated_force.distances_to_walk,
        force.distances_to_walk,
    )


def test_regulated_with_one_cursor_fully_equalizes_temperatures() -> None:
    weighted_vectors = np.array([[1.0, 0.0], [0.5, 0.0]])
    distances_to_walk = np.array([2.0, 1.0])
    force = Force(weighted_vectors=weighted_vectors, distances_to_walk=distances_to_walk)

    regulated_force = force.regulated(regulation_cursor=1)

    regulated_temperatures = regulated_force.maximum_temperatures
    np.testing.assert_allclose(
        regulated_temperatures,
        regulated_temperatures[0],
    )
    np.testing.assert_allclose(
        regulated_force.distances_to_walk,
        force.distances_to_walk,
    )


@pytest.mark.parametrize("regulation_cursor", [0, 0.5, 1])
def test_regulated_with_uniform_temperatures_returns_clone(regulation_cursor: float) -> None:
    weighted_vectors = np.array([[1.0, 0.0], [1.0, 0.0]])
    distances_to_walk = np.array([2.0, 2.0])
    force = Force(weighted_vectors=weighted_vectors, distances_to_walk=distances_to_walk)

    regulated_force = force.regulated(regulation_cursor=regulation_cursor)

    np.testing.assert_allclose(
        regulated_force.weighted_vectors,
        force.weighted_vectors,
    )
    np.testing.assert_allclose(
        regulated_force.distances_to_walk,
        force.distances_to_walk,
    )


@pytest.mark.parametrize(
    "weighted_vectors, distances_to_walk, expected_temps, regulation_cursor,"
    " expected_regulated_temps",
    [
        (
            np.array([[2.0, 0.0], [3.0, 0.0]]),
            np.array([1.0, 6.0]),
            np.array([1, 4]),
            0,
            np.array([1, 4]),
        ),
        (
            np.array([[2.0, 0.0], [3.0, 0.0]]),
            np.array([1.0, 6.0]),
            np.array([1, 4]),
            0.5,
            np.array([1, 2]),
        ),
        (
            np.array([[2.0, 0.0], [3.0, 0.0]]),
            np.array([1.0, 6.0]),
            np.array([1, 4]),
            1,
            np.array([1, 1]),
        ),
        (
            np.array([[2.0, 0.0], [3.0, 0.0], [6.0, 0.0]]),
            np.array([1.0, 6.0, 12.0]),
            np.array([1, 4, 4]),
            0.5,
            np.array([1, 2.828, 2]),
        ),
        (
            np.array([[2.0, 0.0], [3.0, 0.0], [3.0, 0.0]]),
            np.array([1.0, 6.0, 12.0]),
            np.array([1, 4, 8]),
            0.5,
            np.array([1, 2, 2.828]),
        ),
    ],
)
def test_regulated_reduces_temperature_spread(
    weighted_vectors: np.ndarray,
    distances_to_walk: np.ndarray,
    expected_temps: np.ndarray,
    regulation_cursor: float,
    expected_regulated_temps: np.ndarray,
) -> None:
    force = Force(weighted_vectors=weighted_vectors, distances_to_walk=distances_to_walk)
    temps = force.maximum_temperatures
    np.testing.assert_allclose(
        temps / np.min(temps),
        expected_temps,
    )

    regulated_force = force.regulated(regulation_cursor=regulation_cursor)
    regulated_temps = regulated_force.maximum_temperatures

    np.testing.assert_allclose(
        regulated_temps / np.min(regulated_temps),
        expected_regulated_temps,
        rtol=1e-2,
    )

    np.testing.assert_allclose(regulated_force.distances_to_walk, force.distances_to_walk)
