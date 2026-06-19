from __future__ import annotations

import numpy as np


class BladeException(Exception):
    pass


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
