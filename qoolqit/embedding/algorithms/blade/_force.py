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
    return np.power(x, stiffness) / (np.power(x, stiffness) + c * np.power(1 - x, stiffness))


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
    weighted_vectors: np.ndarray
    distances_to_walk: np.ndarray

    def __post_init__(self) -> None:
        assert self.weighted_vectors.shape[:-1] == self.distances_to_walk.shape
        assert not np.any(np.isnan(self.weighted_vectors))
        self.maximum_temperatures

    def get_nb_dims(self) -> int:
        return len(self.weighted_vectors.shape)

    def _fit_to_dims(self, a: np.ndarray) -> np.ndarray:
        return a.reshape((*a.shape, *((1,) * (self.get_nb_dims() - len(a.shape)))))

    def regulated(
        self,
        regulation_cursor: float = 0,
    ) -> "Force":
        min_temperature = np.min(self.maximum_temperatures)

        if min_temperature != np.inf:
            temperature_ratios = self.maximum_temperatures / min_temperature
            weight_ratios = self.vector_weights / np.max(self.vector_weights)
            used_cursors = clip_modulate_cursor(
                strong_cursor=regulation_cursor, weak_cursor=weight_ratios
            )
            regulated_temperature_ratios = temperature_ratios ** (1 - used_cursors)

            regulated_weighted_vectors = (
                self.weighted_vectors
                * np.where(
                    self.weighted_vectors == 0,
                    np.zeros_like(self.weighted_vectors),
                    self._fit_to_dims(temperature_ratios),
                )
                / self._fit_to_dims(regulated_temperature_ratios)
            )

        else:
            regulated_weighted_vectors = np.zeros_like(self.weighted_vectors)

        return Force(
            weighted_vectors=regulated_weighted_vectors,
            distances_to_walk=self.distances_to_walk,
        )

    @cached_property
    def vector_weights(self) -> np.ndarray:
        return np.linalg.norm(self.weighted_vectors, axis=self.get_nb_dims() - 1)

    @cached_property
    def maximum_temperatures(self) -> np.ndarray:
        vector_weights = self.vector_weights
        with np.errstate(divide="ignore", invalid="ignore"):
            maximum_temperatures = self.distances_to_walk / vector_weights
        maximum_temperatures[vector_weights == 0] = np.inf

        assert np.all(
            (
                maximum_temperatures[np.triu_indices_from(maximum_temperatures, k=1)]
                if maximum_temperatures.ndim == 2
                else maximum_temperatures
            )
            > 0
        )
        return maximum_temperatures

    def get_temperature(self) -> Any | int:
        maximum_temperatures = self.maximum_temperatures
        logger.debug(f"{maximum_temperatures=}")

        min_temperature = np.min(maximum_temperatures)

        # the next condition fixes the case where at some index, weighted_vectors is almost zero,
        # and squared in vector_weights it becomes 0
        # (but distances_to_walk is not zero so the force will be infinite)
        return min_temperature if min_temperature != np.inf else 0

    def get_forces(self, temperature: float) -> np.ndarray:
        with np.errstate(divide="ignore", invalid="ignore"):
            forces = temperature * self.weighted_vectors
        forces[self.weighted_vectors == 0] = 0
        return forces

    def get_resulting_forces(self, temperature: float) -> np.ndarray:
        forces = self.get_forces(temperature)

        if self.get_nb_dims() == 3:
            return np.sum(forces, axis=1)
        else:
            return forces
