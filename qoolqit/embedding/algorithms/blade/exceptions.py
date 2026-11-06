"""Exceptions raised by the BLaDE embedding algorithm."""

from __future__ import annotations

import numpy as np


class BladeException(Exception):
    """Base class for exceptions raised by the BLaDE algorithm."""


class DistanceRatioException(BladeException):
    """Raised when an optimization constraint could not be satisfied.

    The partial result is still accessible via the `result` attribute,
    and may be used or plotted by the user.

    Attributes:
        result: The positions computed by the algorithm despite the unmet constraint.
    """

    def __init__(
        self, *, required_ratio: float, output_ratio: float, positions: np.ndarray
    ) -> None:
        """Initialize the exception with the distance ratios and the computed positions."""
        super().__init__(
            f"The output distance ratio {output_ratio} of BLaDE is higher than the "
            f"required {required_ratio}. "
            "You may still access the positions via the `positions` attribute of this exception.",
        )
        self._positions = positions

    @property
    def positions(self) -> np.ndarray:
        """The positions computed by the algorithm despite the unmet constraint."""
        return self._positions


class DuplicatePositionsError(BladeException):
    """Raised when two nodes have identical positions (zero pairwise distance).

    Attributes:
        step: Index of the step whose input positions contain a duplicate, i.e. the
            duplicate was produced by the previous step (or by the initialization or
            the PCA for the first step of a round).
        min_distance: The minimum pairwise distance found.
    """

    def __init__(self, *, step: int, min_distance: float) -> None:
        """Initialize the exception with the step and the minimum pairwise distance."""
        super().__init__(
            f"BLaDE produced duplicate positions: minimum pairwise distance {min_distance!r} "
            f"in the input positions of step {step}."
        )
        self.step = step
        self.min_distance = min_distance
