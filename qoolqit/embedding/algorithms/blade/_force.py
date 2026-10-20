from __future__ import annotations

import dataclasses
import logging
from functools import cached_property
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

logger = logging.getLogger(__name__)


def configured_increasing_func(
    x: ArrayLike, *, middle_value: float = 0.5, stiffness: float = 1.0
) -> np.ndarray:
    """Increasing function from [0, 1] to [0, 1]."""
    c = 1 / middle_value - 1
    x = np.asarray(x, dtype=float)
    powered_x = x**stiffness
    return powered_x / (powered_x + c * (1 - x) ** stiffness)


def modulate_cursor(
    *,
    strong_cursor: ArrayLike,
    weak_cursor: ArrayLike,
    center_value: float = 0.25,
    stiffness: float = 1.0,
) -> np.ndarray:
    strong_cursor = np.asarray(strong_cursor, dtype=float)
    weak_cursor = np.asarray(weak_cursor, dtype=float)

    weak_coeff_multiplier = configured_increasing_func(
        weak_cursor, middle_value=1 / (1 / center_value - 1), stiffness=stiffness
    )

    return (
        strong_cursor
        * weak_coeff_multiplier
        / np.where(
            (strong_cursor == 1) & (weak_cursor == 0),
            np.inf,
            (1 + strong_cursor * (weak_coeff_multiplier - 1)),
        )
    )


def clip_modulate_cursor(
    *,
    strong_cursor: ArrayLike,
    weak_cursor: ArrayLike,
    center_value: float = 0.25,
    stiffness: float = 1.0,
) -> np.ndarray:
    value = modulate_cursor(
        strong_cursor=strong_cursor,
        weak_cursor=weak_cursor,
        center_value=center_value,
        stiffness=stiffness,
    )
    return np.clip(value, 0, 1)


@dataclasses.dataclass(frozen=True)
class Force:
    """Forces along the directions defined by node positions.

    Each force is a signed weight along a unit vector, so that only scalar arrays are stored:
    - pairwise forces are (N, N) arrays: the force of the pair (i, j) applied on the node i
      is `weights[i, j] * (positions[j] - positions[i]) / distances[i, j]`;
    - node forces are (N,) arrays: the force applied on the node i is
      `weights[i] * positions[i] / distances[i]`, `distances` being the norms of the positions.
    Forces whose distance is zero (e.g. the pair (i, i)) have no direction and are set to zero.
    """

    weights: np.ndarray
    distances_to_walk: np.ndarray
    positions: np.ndarray
    distances: np.ndarray

    def __post_init__(self) -> None:
        """Check values, shapes and cleaning and caching."""
        assert self.weights.shape == self.distances_to_walk.shape == self.distances.shape
        assert np.all(np.isfinite(self.distances_to_walk))
        assert np.all(np.isfinite(self.weights))
        cleaned = np.where(self.distances == 0, 0.0, self.weights)
        object.__setattr__(self, "weights", cleaned)
        self.maximum_temperatures  # noqa: B018

    def regulated(
        self,
        regulation_cursor: float = 0,
    ) -> Force:
        min_temperature = np.min(self.maximum_temperatures)

        if min_temperature != np.inf:
            temperature_ratios = self.maximum_temperatures / min_temperature
            weight_ratios = self.vector_weights / np.max(self.vector_weights)
            used_cursors = clip_modulate_cursor(
                strong_cursor=regulation_cursor, weak_cursor=weight_ratios
            )
            regulated_temperature_ratios = temperature_ratios ** (1 - used_cursors)

            regulated_weights = (
                self.weights
                * np.where(self.weights == 0, 0, temperature_ratios)
                / regulated_temperature_ratios
            )

        else:
            regulated_weights = np.zeros_like(self.weights)

        return dataclasses.replace(self, weights=regulated_weights)

    @cached_property
    def vector_weights(self) -> np.ndarray:
        return np.abs(self.weights)

    @cached_property
    def maximum_temperatures(self) -> np.ndarray:
        vector_weights = self.vector_weights
        with np.errstate(divide="ignore", invalid="ignore"):
            maximum_temperatures = self.distances_to_walk / vector_weights
        maximum_temperatures[vector_weights == 0] = np.inf

        assert np.all(maximum_temperatures > 0)
        return maximum_temperatures

    def get_temperature(self) -> Any | int:
        maximum_temperatures = self.maximum_temperatures
        logger.debug("maximum_temperatures=%r", maximum_temperatures)

        min_temperature = np.min(maximum_temperatures)

        # the next condition fixes the case where all the weights are zero
        # (no force to apply, the temperature is not limited)
        return min_temperature if min_temperature != np.inf else 0

    def get_resulting_forces(self, temperature: float) -> np.ndarray:
        """Return the (N, d) resulting force vectors applied on the nodes."""
        coefficients = np.divide(
            temperature * self.weights,
            self.distances,
            out=np.zeros_like(self.weights),
            where=(self.distances != 0),
        )

        if coefficients.ndim == 2:
            # sum over j of coefficients[i, j] * (positions[j] - positions[i])
            return (
                coefficients @ self.positions
                - np.sum(coefficients, axis=1)[:, np.newaxis] * self.positions
            )
        else:
            return coefficients[:, np.newaxis] * self.positions
